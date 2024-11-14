# CRM DDD PoC

- [CRM DDD PoC](#crm-ddd-poc)
  - [Project description](#project-description)
    - [Key features](#key-features)
  - [Links](#links)
    - [Demo](#demo)
  - [Tech stack](#tech-stack)
  - [Getting started](#getting-started)
  - [User stories](#user-stories)
    - [Customer Management](#customer-management)
    - [Contact Management](#contact-management)
    - [Lead and Opportunity Management](#lead-and-opportunity-management)
    - [Salesmen Management](#salesmen-management)
    - [User and Role Management](#user-and-role-management)

## Project description

Project for learning the concept of Domain Driven Design.

Customer Relationship Management (CRM) application.

### Key features

- customer management,
- leads and opportunities tracking,
- sales representatives management,
- role-based authentication.

## Links

### Demo

not yet available

## Tech stack

- Python 3.12
- FastAPI
- SQLAlchemy + PostgreSQL 15
- Docker

## Getting started

In the project directory, create _.env_ file and add the required values (you can see _.env.example_ file for reference).

Run `docker-compose up` to run the development server.

Access the API documentation at http://localhost:8000/docs#/.

To fill the database with example data, run `python ./scripts/populate_db.py populate-db sql` in the web container terminal.

To run tests, run these commands:

- `make test_unit` - for unit tests,
- `make test_integration` - for integration tests,
- `make test_all` - for all tests.

## User stories

### Customer Management

1. **Create Customer**

   - **As a** sales representative, **I want** to create a new customer record **so that** I can track their information and interactions.

2. **Edit Customer Information**

   - **As a** sales representative, **I want** to edit an existing customer's information **so that** I can keep their data up-to-date.

3. **View Customer Details**

   - **As a** sales representative, **I want** to view a customer's details **so that** I can quickly access all relevant information during interactions.

4. **Search Customers**
   - **As a** sales representative, **I want** to search for customers by company name, industry, or other criteria **so that** I can quickly find the customer I'm looking for.

### Contact Management

5. **Add Contact to Customer**

   - **As a** sales representative, **I want** to add a contact to a customer's profile **so that** I can record key people within an organization.

6. **Edit Contact Information**

   - **As a** sales representative, **I want** to edit a contact's information **so that** their details are accurate and current.

7. **Delete Contact**
   - **As a** sales representative, **I want** to delete a contact from a customer's profile **so that** I can remove outdated or incorrect information.

### Lead and Opportunity Management

8. **Create Lead**

   - **As a** sales representative, **I want** to create a lead in the system **so that** potential customers can be tracked and managed.

9. **Convert Lead to Customer**

   - **As a** sales representative, **I want** to convert a lead to a customer **so that** we can officially start tracking them as a customer.

10. **Assign Lead to Salesman**

    - **As a** sales representative, **I want** to assign a new lead to me or to transfer the lead to the other sales representative **so that** the lead can be effectively managed and followed up by the appropriate team member.

11. **Track Opportunities**

    - **As a** sales representative, **I want** to track sales opportunities **so that** I can monitor potential revenue and sales progress.

12. **Update Opportunity Status**

    - **As a** sales representative, **I want** to update the status of an opportunity (e.g., proposal sent, negotiation, won/lost) **so that** the sales pipeline is accurately reflected.

13. **Add Notes to Leads and Opportunities**

    - **As a** sales representative, **I want** to add notes to my leads and opportunities **so that** I can keep track of important details, interactions, and updates.

### Salesmen Management

14. **Create Accounts Associated with Salesmen**

    - **As a** system administrator, **I want** to create accounts for sales representatives **so that** salesmen will be able to login to their account and perform actions on their behalf.

15. **Update Salesmen Data**

    - **As a** sales representative, **I want** to edit my personal information **so that** I can keep my data up-to-date.

### User and Role Management

16. **Role-Based Access Control**

    - **As a** system administrator, **I want** to assign roles and permissions to users **so that** access to certain features is restricted based on their role.
