import re

import graphene
from graphene import Decimal
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from decimal import Decimal as D
from crm.models import Customer, Order, Product
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from crm.filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (relay.Node,)
        fields = "__all__"  # Explicitly expose all model fields


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info, input):
        try:
            if Customer.objects.filter(email=input.email).exists():
                raise Exception("Email already exists")
            if input.phone and not re.match(
                r"^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$", input.phone
            ):
                raise Exception("Invalid phone format")
            customer = Customer(
                name=input.name, email=input.email, phone=input.phone or ""
            )
            customer.save()
            return CreateCustomer(
                customer=customer, message="Customer created successfully", success=True
            )
        except Exception as e:
            return CreateCustomer(customer=None, message=str(e), success=False)


class BulkCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(BulkCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success = graphene.Boolean()

    def mutate(self, info, input):
        created = []
        errors = []

        for i, customer_input in enumerate(input):
            try:
                if Customer.objects.filter(email=customer_input.email).exists():
                    raise Exception(f"Email already exists: {customer_input.email}")
                if customer_input.phone and not re.match(
                    r"^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$", customer_input.phone
                ):
                    raise Exception(f"Invalid phone format: {customer_input.phone}")

                customer = Customer(
                    name=customer_input.name,
                    email=customer_input.email,
                    phone=customer_input.phone or "",
                )
                customer.save()
                created.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(
            customers=created, errors=errors, success=len(errors) == 0
        )


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = Decimal(required=True)  # Back to Decimal type
    stock = graphene.Int()


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info, input):
        try:
            try:
                price = D(input.price)
                if price <= 0:
                    raise Exception("Price must be a positive value.")
                if input.stock < 0:
                    raise Exception("Stock cannot be negative.")
                product = Product(name=input.name, price=price, stock=input.stock or 0)
            except:
                raise Exception("Invalid price format")
            product.save()
            return CreateProduct(
                product=product, message="Product created successfully", success=True
            )
        except Exception as e:
            return CreateProduct(product=None, message=str(e), success=False)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(order=None, message="Invalid customer ID", success=False)

        if not input.product_ids:
            return CreateOrder(
                order=None,
                message="At least one product must be selected",
                success=False,
            )

        products = []
        total = 0
        for pid in input.product_ids:
            try:
                product = Product.objects.get(pk=pid)
                total += float(product.price)
                products.append(product)
            except Product.DoesNotExist:
                return CreateOrder(
                    order=None, message=f"Invalid product ID: {pid}", success=False
                )

        order = Order(customer=customer, total_amount=total)
        if input.order_date:
            order.order_date = input.order_date
        order.save()
        order.products.set(products)
        return CreateOrder(
            order=order, message="Order created successfully", success=True
        )


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class CustomerFilterInput(graphene.InputObjectType):
    nameIcontains = graphene.String()
    emailIcontains = graphene.String()
    createdAtGte = graphene.Date()
    createdAtLte = graphene.Date()
    phonePattern = graphene.String()


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter,
        order_by=graphene.String(description="Order by a field, e.g., 'name' or '-created_at'")
    )
    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter,
        order_by=graphene.String(description="Order by a field, e.g., 'price' or '-stock'")
    )
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter,
        order_by=graphene.String(description="Order by a field, e.g., 'order_date' or '-total_amount'")
    )

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        return qs.order_by(order_by) if order_by else qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        return qs.order_by(order_by) if order_by else qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        return qs.order_by(order_by) if order_by else qs