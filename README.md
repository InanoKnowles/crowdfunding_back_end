# Crowdfunding Back End
This crowdfunding application was completed as part of She Codes Australia's Plus Program that goes for 6 months for women.
The technologies used are as follows:
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.1-darkgreen)
![Django REST](https://img.shields.io/badge/Django_REST_Framework-3.15-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Heroku](https://img.shields.io/badge/Deployed_on-Heroku-purple)


## Project Details:
| Project Name:       | Shelter                                                                             |
| :------------------ | :---------------------------------------------------------------------------------- |
| App Link:           | [Shelter Website](https://inanos-crowdfunding-back-end-aa6cc4b6f11a.herokuapp.com/) |
| Target Audience(s): | Homeless People in Australia                                                        |
| Website Uses:       | Users can create and browse fundraisers, and support them by making pledges.        |


[Add a table of contents here]

### How to create a user account on insomnia:
POST request on Insomnica
enter this url https://inanos-crowdfunding-back-end-aa6cc4b6f11a.herokuapp.com/users/

**The minimum JSON details required:**
```
{
  "username": "enterUserName",
  "first_name": "enterFirstName",
  "last_name": "enterLastName",
  "email": "enterEmailAddress"
}
```
To get a token for that user:
https://inanos-crowdfunding-back-end-aa6cc4b6f11a.herokuapp.com/api-token-auth/

Use the details of the user that was just made
```
{
  "username": "newuser",
  "password": "StrongPassword123"
}
```

and you should get this success message, details will differ:
```
{
  "token": "abc123...",
  "user_id": 4,
  "email": "newuser@example.com"
}
```

## Project Requirements (Part 1)
- [x] Build an API using Django and Django Rest Framework (DRF)

- [x] **Users can make an account, should atleast have:**
  - [x] Username
  - [x] Email Address
  - [x] Password

- [x] **Users have the ability to create a fundraiser, should have the following attributes:**
  - [x] Title
  - [x] Owner (The User who made the fundraiser)
  - [x] Description of the fundraiser
  - [x] Image
  - [x] Target amount to raise
  - [x] Open or Closed to accepting supporters through pledges
  - [x] Date and time the fundraiser was created  

- [x] **Users can create pledges to support a fundraiser, which include the following attributes:**
  - [x] Amount willing to pledge to the fundraiser
  - [x] The fundraiser that the pledge is for
  - [x] The supporter's name (The User who made the pledge)
  - [x] The User has the ability to choose if they want their pledge to be anonymous or not
  - [x] A comment to go along with the pledge from the user based on if they are anonymous or not

**Authentication & Permissions**
- [ ] Rules around update and delete functionality for fundraisers, pledges, comments and User accounts
- [ ] Return relevant status codes for both successful and unsuccessful requests to the API, gracefully
- [ ] Use token authentication with an endpoint that returns a token and the current user’s details

:no_good_woman: This project does not handle real money transactions. :no_good_woman:

## Additional Features I've Added:
- Search for all (or any one of the following) fundraisers, pledges, comments and users that exist in the database. Filter by categories (eg: open to pledges, less than $200.00, within 5KM of locaition)
- Take the total monetary value of all the Pledges and show how much moeny is left to reach the goal
- Calculate how many days are left until the deadline date and time has been reached

## API Spec
|   |   |
|---|---|
|   |   |
