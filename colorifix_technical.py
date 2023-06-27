from typing import Union
from fastapi import FastAPI
from neo4j import GraphDatabase
import pandas as pd

# PART 1 - DATA MODEL

# clean the data

#data = pd.read_csv('/Users/christopherbacon/Documents/projects/Colorifix/data.csv',sep='|')

# def remove_redundant_cols(df):
#     dropped_cols_df = df.drop(columns=['Unnamed: 0','Unnamed: 7'])
#     return dropped_cols_df

# def remove_redundant_rows(df):
#     dropped_rows_df = df.drop(axis=0, index=0)
#     return dropped_rows_df

# def capitalise_words(entry):
#     return entry.title()

# def remove_second_word(entry):
#     words = entry.split()
#     if len(words) > 1:
#         return words[0]

# def remove_first_word(entry):
#     words = entry.split()
#     if len(words) >1:
#         return words[1]
    

# # Not sure whether I need to do this yet
# # data['PermissionNameDescription'] = data['PermissionNameDescription'].map(remove_second_word)
# data_redundant_cols_removed = remove_redundant_cols(data)
# data = data_redundant_cols_removed.applymap(capitalise_words)
# print(data)

# Make the data model

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session() as session:
    # Delete all nodes and relationships
    session.run("MATCH (n) DETACH DELETE n")


def build_data_model():
    with driver.session() as session:
        # create User nodes
        create_users_query = """
            UNWIND $users AS user
            MERGE (u:User {username: user.UserName})
        """
        users = [
            {"UserName": "admin@my-company.com"},
            {"UserName": "user@my-company.com"}
        ]
        session.run(create_users_query, users=users)

        #create company nodes
        create_companies_query = """
            UNWIND $companies AS company
            MERGE (c:Company {companyName: company.CompanyName})
        """
        companies = [
            {"CompanyName": "MyCompany"}
        ]
        session.run(create_companies_query, companies=companies)


        # create Permission Group nodes
        create_permission_group_query = """
            UNWIND $permissionGroups AS permission
            MERGE (p:PermissionGroup {permissionGroup: permission.PermissionGroupDescription})
        """
        permissionGroups = [
            {"PermissionGroupDescription": "Admin"},
            {"PermissionGroupDescription": "User"}
        ]
        session.run(create_permission_group_query, permissionGroups=permissionGroups)


        # create permissions nodes
        create_permissions_query = """
            UNWIND $permissions AS permission
            MERGE (a:Permission {permission: permission.PermissionName})
        """
        permissions = [
            {"PermissionName": "Add Companies"},
            {"PermissionName": "Edit Companies"},
            {"PermissionName": "Delete Companies"},
            {"PermissionName": "View Companies"},
            {"PermissionName": "Add Users"},
            {"PermissionName": "Edit Users"},
            {"PermissionName": "Delete Users"},
            {"PermissionName": "View Users"}
        ]
        session.run(create_permissions_query, permissions=permissions)

        # Create relationships between Permisison Group and Permission nodes
        create_permission_relationships_query = """
            MATCH (p:PermissionGroup {permissionGroup: $permissionGroupName})
            MATCH (a:Permission {permission: $permissionName})
            CREATE (p)-[:HAS_PERMISSION]->(a)
        """
        permissions_relationships = [
            {"permissionGroupName": "Admin", "permissionName": "Add Companies"},
            {"permissionGroupName": "Admin", "permissionName": "Edit Companies"},
            {"permissionGroupName": "Admin", "permissionName": "Delete Companies"},
            {"permissionGroupName": "Admin", "permissionName": "View Companies"},
            {"permissionGroupName": "Admin", "permissionName": "Add Users"},
            {"permissionGroupName": "Admin", "permissionName": "Edit Users"},
            {"permissionGroupName": "Admin", "permissionName": "Delete Users"},
            {"permissionGroupName": "Admin", "permissionName": "View Users"},
            {"permissionGroupName": "User", "permissionName": "View Companies"},
            {"permissionGroupName": "User", "permissionName": "View Users"}
        ]
        for relationship in permissions_relationships:
            session.run(create_permission_relationships_query, **relationship)

        # Create relationships between Users and Permission groups
        create_user_permissions_query = """
            MATCH (u:User {username: $userName})
            MATCH (p:PermissionGroup {permissionGroup: $permissionGroupName})
            CREATE (u)-[:IN_PERMISSION_GROUP]->(p)
        """
        users_relationships = [
            {"userName": "admin@my-company.com", "permissionGroupName": "Admin"},
            {"userName": "user@my-company.com", "permissionGroupName": "User"}
        ]
        for relationship in users_relationships:
            session.run(create_user_permissions_query, **relationship)


        # Create relationships between Users and Permission groups
        create_user_company_query = """
            MATCH (u:User {username: $userName})
            MATCH (c:Company {companyName: $company})
            CREATE (u)-[:WORKS_FOR]->(c)
        """
        company_relationships = [
            {"userName": "admin@my-company.com", "company": "MyCompany"},
            {"userName": "user@my-company.com", "company": "MyCompany"}
        ]
        for relationship in company_relationships:
            session.run(create_user_company_query, **relationship)


# Call the import_data function
build_data_model()

# Close the Neo4j driver
driver.close()



# # PART 2 Create REST API

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


