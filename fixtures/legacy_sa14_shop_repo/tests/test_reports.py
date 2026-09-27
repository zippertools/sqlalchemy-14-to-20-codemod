from __future__ import annotations

from legacy_shop.models import Base, Customer, Invoice
from legacy_shop.reports import (
    create_invoice_statement,
    customer_invoice_rows,
    delete_invoice_statement,
    get_customer,
    mark_invoice_paid_statement,
    paid_customers_with_invoices,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def _seed(session: Session) -> Customer:
    customer = Customer(email="ada@example.com", name="Ada Lovelace")
    customer.invoices.append(Invoice(status="paid", total_cents=12900))
    customer.invoices.append(Invoice(status="draft", total_cents=4500))
    session.add(customer)
    session.commit()
    return customer


def test_get_customer_uses_legacy_query_get() -> None:
    session = _session()
    customer = _seed(session)

    loaded = get_customer(session, customer.id)

    assert loaded is not None
    assert loaded.email == "ada@example.com"


def test_customer_invoice_rows_uses_legacy_select_list() -> None:
    session = _session()
    _seed(session)

    assert customer_invoice_rows(session) == [("ada@example.com", 12900)]


def test_paid_customers_uses_string_join_and_loader_option() -> None:
    session = _session()
    _seed(session)

    customers = paid_customers_with_invoices(session)

    assert len(customers) == 1
    assert customers[0].invoices[0].total_cents == 12900


def test_dml_constructor_kwargs() -> None:
    session = _session()
    customer = _seed(session)

    insert_statement = create_invoice_statement(
        Invoice.__table__,
        customer.id,
        9900,
    )
    result = session.execute(insert_statement)
    invoice_id = result.inserted_primary_key[0]
    session.execute(
        mark_invoice_paid_statement(Invoice.__table__, int(invoice_id)),
    )
    session.commit()

    rows = customer_invoice_rows(session)
    assert ("ada@example.com", 9900) in rows

    session.execute(delete_invoice_statement(Invoice.__table__, int(invoice_id)))
    session.commit()
    assert session.query(Invoice).get(invoice_id) is None
