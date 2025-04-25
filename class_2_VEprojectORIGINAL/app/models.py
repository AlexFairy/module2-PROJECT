from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from typing import List, Optional

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

service_ticket_inventory = Table(
    "service_ticket_inventory",
    Base.metadata,
    Column("service_ticket_id", ForeignKey("service_tickets.id"), primary_key=True),
    Column("inventory_id", ForeignKey("inventory.id"), primary_key=True))

class Customers(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(45), nullable=False)
    phone_number: Mapped[str] = mapped_column(db.String(15), nullable=False)
    car_brand: Mapped[str] = mapped_column(db.String(30), nullable=False)
    car_type: Mapped[str] = mapped_column(db.String(30), nullable=False)
    car_mileage: Mapped[int] = mapped_column(nullable=False)
    mechanical_issue: Mapped[str] = mapped_column(db.String(250), nullable=False)
    email: Mapped[str] = mapped_column(db.String(45), nullable=False)
    password: Mapped[str] = mapped_column(db.String(15), nullable=False)

    #one to many
    service_tickets: Mapped[List["ServiceTickets"]] = relationship(back_populates="customer")

class Mechanic(Base):
    __tablename__ = "mechanic"

    id: Mapped[int] = mapped_column(primary_key=True)
    mechanic_name: Mapped[str] = mapped_column(db.String(45), nullable=False)
    email: Mapped[str] = mapped_column(db.String(65), nullable=False)
    address: Mapped[str] = mapped_column(db.String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(db.String(15), nullable=False)
    salary: Mapped[float] = mapped_column(nullable=False)

    #one to many
    service_tickets: Mapped[List["ServiceTickets"]] = relationship(back_populates="mechanic")

class ServiceTickets(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_description: Mapped[str] = mapped_column(db.String(250), nullable=False)
    cost: Mapped[float] = mapped_column(nullable=False)
    vin_number: Mapped[str] = mapped_column(db.String(17), nullable=False)
    work_complete: Mapped[bool] = mapped_column(nullable=False, default=False)
    car_submission_date: Mapped[date] = mapped_column(nullable=False)
    work_start_date: Mapped[Optional[date]] = mapped_column()
    work_finish_date: Mapped[Optional[date]] = mapped_column()

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    mechanic_id: Mapped[int] = mapped_column(ForeignKey("mechanic.id"), nullable=False)

    customer: Mapped["Customers"] = relationship("Customers", back_populates="service_tickets")
    mechanic: Mapped["Mechanic"] = relationship("Mechanic", back_populates="service_tickets")

    #many to many
    inventory_items: Mapped[List["Inventory"]] = relationship("Inventory", secondary=service_ticket_inventory, back_populates="service_tickets")

class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(55), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)

    #many to many
    service_tickets: Mapped[List["ServiceTickets"]] = relationship("ServiceTickets", secondary=service_ticket_inventory, back_populates="inventory_items")