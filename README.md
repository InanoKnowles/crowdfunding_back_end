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

## Table of Contents:
- [Crowdfunding Back End](#crowdfunding-back-end)
  - [Project Details:](#project-details)
  - [Table of Contents:](#table-of-contents)
    - [How to create a User Account on Insomnia:](#how-to-create-a-user-account-on-insomnia)
  - [Project Requirements (Part 1)](#project-requirements-part-1)
  - [Additional Features I've Added:](#additional-features-ive-added)
  - [API Spec](#api-spec)
  - [End Point Demonstration](#end-point-demonstration)
  - [Database Schema](#database-schema)



### How to create a User Account on Insomnia:
1. POST request on Insomnia
2. Enter this url: https://inanos-crowdfunding-back-end-aa6cc4b6f11a.herokuapp.com/users/
3. {
     "username": "enterUserName",
     "first_name": "enterFirstName",
     "last_name": "enterLastName",
     "email": "enterEmailAddress"
   }


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
- [x] Rules around update and delete functionality for fundraisers, pledges, comments and User accounts
- [x] Return relevant status codes for both successful and unsuccessful requests to the API, gracefully
- [x] Use token authentication with an endpoint that returns a token and the current user’s details


:no_good_woman: This project does not handle real money transactions. :no_good_woman:


## Additional Features I've Added:
- [x] Search for all (or any one of the following) fundraisers, pledges, comments and users that exist in the database. 
- [x] Filter by categories (eg: open to pledges, less than $200.00, within 5KM of locaition)
- [x] Take the total monetary value of all the Pledges and show how much money is left to reach the goal
- [x] Calculate how many days are left until the deadline date and time has been reached


## API Spec
| URL                | HTTP Method | Purpose                                        | Request Body                                                                                                      | Success Response Code  | Authentication/Authorisation |
| ------------------ | ----------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ---------------------- | ---------------------------- |
| /users/            | GET         | List all user accounts                         | None                                                                                                              | 200 OK                 | Public (read-only)           |
| /users/            | POST        | Create a new user account                      | `{ "username": "", "email": "", "password": "" }`                                                                 | 201 Created            | Public                       |
| /users/<id>/       | GET         | Retrieve a single user account                 | None                                                                                                              | 200 OK                 | Public (read-only)           |
| /api-token-auth/   | POST        | Log in and receive auth token and user details | `{ "username": "", "password": "" }`                                                                              | 200 OK                 | Public                       |
| /fundraisers/      | GET         | List all fundraisers                           | None                                                                                                              | 200 OK                 | Public (read-only)           |
| /fundraisers/      | POST        | Create a fundraiser                            | `{ "title": "", "description": "", "goal": 0, "image": "", "is_open": true, "deadline": "YYYY-MM-DDTHH:MM:SSZ" }` | 201 Created            | Token required               |
| /fundraisers/<id>/ | GET         | Retrieve fundraiser details                    | None                                                                                                              | 200 OK                 | Public (read-only)           |
| /fundraisers/<id>/ | PUT         | Update a fundraiser                            | Partial fundraiser fields (owner and date read-only)                                                              | 200 OK                 | Token required + owner only  |
| /fundraisers/<id>/ | DELETE      | Delete a fundraiser                            | None                                                                                                              | 204 No Content         | Token required + owner only  |
| /pledges/          | GET         | List all pledges                               | None                                                                                                              | 200 OK                 | Public (read-only)           |
| /pledges/          | POST        | Create a pledge                                | `{ "amount": 0, "fundraiser": <id>, "anonymous": false, "comment": "" }`                                          | 201 Created            | Token required               |
| /pledges/<id>/     | GET         | Retrieve a single pledge                       | None                                                                                                              | 200 OK                 | Public (read-only)           |
| /pledges/<id>/     | PUT         | Update a pledge (not permitted)                | Any                                                                                                               | 405 Method Not Allowed | Token required               |
| /pledges/<id>/     | DELETE      | Delete a pledge (not permitted)                | None                                                                                                              | 405 Method Not Allowed | Token required               |
| /comments/         | GET         | List all comments                              | None                                                                                                              | 200 OK                 | Public (read-only)           |
| /comments/         | POST        | Create a comment or reply                      | `{ "fundraiser": <id>, "content": "", "parent": <id or null> }`                                                   | 201 Created            | Token required               |
| /comments/<id>/    | GET         | Retrieve a single comment                      | None                                                                                                              | 200 OK                 | Public (read-only)           |
| /comments/<id>/    | PUT         | Update a comment                               | `{ "content": "" }`                                                                                               | 200 OK                 | Token required + author only |
| /comments/<id>/    | DELETE      | Delete a comment                               | None                                                                                                              | 204 No Content         | Token required + author only |


## End Point Demonstration
![Insomnia API endpoints demo](crowdfunding/insomnia_imgs/all_endpoints.gif)


## Database Schema
| Table          | Primary Key | Fields                                                                         | Foreign Keys                                                                                      |
| -------------- | ----------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **CustomUser** | `id`        | `username`, `email`, `password` (plus other `AbstractUser` fields)             | None                                                                                              |
| **Fundraiser** | `id`        | `title`, `description`, `goal`, `image`, `is_open`, `date_created`, `deadline` | `owner_id → CustomUser.id`                                                                        |
| **Pledge**     | `id`        | `amount`, `comment`, `anonymous`                                               | `fundraiser_id → Fundraiser.id`, `supporter_id → CustomUser.id`                                   |
| **Comment**    | `id`        | `content`, `anonymous`, `date_created`                                         | `fundraiser_id → Fundraiser.id`, `author_id → CustomUser.id`, `parent_id → Comment.id` (nullable) |

| Relationship               | Notation                               | Meaning                                                                               | Connects via                   |
| -------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------ |
| User owns Fundraisers      | `CustomUser (1) ──< Fundraiser (0..*)` | One user can own many fundraisers; each fundraiser has exactly one owner              | `Fundraiser.owner_id`          |
| Fundraiser has Pledges     | `Fundraiser (1) ──< Pledge (0..*)`     | One fundraiser can have many pledges; each pledge belongs to exactly one fundraiser   | `Pledge.fundraiser_id`         |
| User makes Pledges         | `CustomUser (1) ──< Pledge (0..*)`     | One user can make many pledges; each pledge has exactly one supporter                 | `Pledge.supporter_id`          |
| Fundraiser has Comments    | `Fundraiser (1) ──< Comment (0..*)`    | One fundraiser can have many comments; each comment belongs to exactly one fundraiser | `Comment.fundraiser_id`        |
| User writes Comments       | `CustomUser (1) ──< Comment (0..*)`    | One user can write many comments; each comment has exactly one author                 | `Comment.author_id`            |
| Comment replies to Comment | `Comment (0..1) ──< Comment (0..*)`    | A comment may have zero or one parent; a parent comment can have many replies         | `Comment.parent_id` (nullable) |