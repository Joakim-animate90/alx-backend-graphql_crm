# ALX Backend GraphQL CRM

A Customer Relationship Management (CRM) system built with Django and GraphQL.

## Features

- GraphQL API for all CRM operations
- Django backend with PostgreSQL support
- Authentication and authorization
- Customer management
- Contact tracking
- Activity logging

## Installation

1. Clone the repository:
```bash
git clone git@github.com:Joakim-animate90/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Configuration

Configure the following environment variables in `.env`:

```ini
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://user:password@localhost:5432/crm
ALLOWED_HOSTS=localhost,127.0.0.1
```

## GraphQL API

Access the GraphQL playground at `http://localhost:8000/graphql`

### Example Queries

```graphql
query {
  customers {
    id
    name
    email
    contacts {
      id
      name
      phone
    }
  }
}
```

### Example Mutations

```graphql
mutation {
  createCustomer(input: {
    name: "Acme Corp"
    email: "contact@acme.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
    }
  }
}
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

This project uses:
- Black for code formatting
- Flake8 for linting
- isort for import sorting

Run formatting:
```bash
black .
flake8
isort .
```

## Deployment

The project can be deployed to:
- Heroku
- AWS Elastic Beanstalk
- Docker containers

See the `deploy/` directory for deployment scripts and configurations.

## License

MIT
