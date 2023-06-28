from typing import Union
from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
import pandas as pd
import re
import uvicorn

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

def is_valid_email(email):
    # Regular expression pattern for validating email format
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    # Check if the email matches the pattern
    if re.match(pattern, email):
        return True
    else:
        return False

@app.post("/company")
async def add_company(company_name: str):
    if not company_name:
        raise HTTPException(status_code=400, detail="No company name provided please try again.")
    with driver.session() as session:
        session.run("CREATE (:Company {name: $companyName})", companyName=company_name)
    
    return {"message": "Company added successfully"}

@app.post("/permission_group")
async def add_permission_group(permission_group: str, permission: str):
    if not permission_group:
        raise HTTPException(status_code=400, detail="No permission group provided please try again.")
    if not permission:
        raise HTTPException(status_code=400, detail="No permission provided please try again.")
    with driver.session() as session:
        session.run("""CREATE (p:PermissionGroup {permissionGroup: $permGroup})
                        MATCH (p:PermissionGroup {permissionGroup: $permGroup})
                        MATCH (a:Permission {permission: $permissionName})
                        CREATE (p)-[:HAS_PERMISSION]->(a)""", permGroup=permission_group, permissionName=permission)

@app.post("/user")
async def add_user(user_email: str, company: str, permissionGroup:str):
    email_bool = is_valid_email(user_email)
    if email_bool == False:
        raise HTTPException(status_code=400, detail="Invalid email please try again.")
    
    with driver.session() as session:
        company_check_query = f"MATCH (c:Company) WHERE c.companyName = $company RETURN n LIMIT 1"
        valid_company = session.run(company_check_query,company=company)
        if not bool(valid_company):
            raise HTTPException(status_code=400, detail="Invalid company please try again.")
    
    with driver.session() as session:
        permission_group_check_query = f"MATCH (p:PermissionGroup) WHERE p.permissionGroup = $permissionGroup RETURN n LIMIT 1"
        valid_permisison_group = session.run(permission_group_check_query, permissionGroup=permissionGroup)
        if not bool(valid_permisison_group):
            raise HTTPException(status_code=400, detail="Invalid permission group please try again.")
    
   
    session.run("""CREATE (u:User {username: $user_name}))
                       MATCH (u:User {username: $user_name})
                       MATCH (a:PermissionGroup {permissionGroup: $permissionGroupName}))
                       CREATE (u)-[:IN_PERMISSION_GROUP]->(p)
                       MATCH (u:User {username: $userName})
                       MATCH (c:Company {companyName: $company})
                       CREATE (u)-[:WORKS_FOR]->(c)
                    """,user_name=user_email, permissionGroupName=permissionGroup, company=company)

# # PART 2 Create REST API

app = FastAPI()



@app.post("/company")
async def add_company(company_name: str):
    if not company_name:
        raise HTTPException(status_code=400, detail="No company name provided please try again.")
    with driver.session() as session:
        session.run("CREATE (:Company {name: $companyName})", companyName=company_name)
    
    return {"message": f"Company: {company_name} added successfully"}

@app.post("/permission_group")
async def add_permission_group(permission_group: str, permission: str):
    if not permission_group:
        raise HTTPException(status_code=400, detail="No permission group provided please try again.")
    if not permission:
        raise HTTPException(status_code=400, detail="No permission provided please try again.")
    with driver.session() as session:
        session.run("""CREATE (p:PermissionGroup {permissionGroup: $permGroup})
                        WITH p
                        MATCH (a:Permission {permission: $permissionName})
                        CREATE (p)-[:HAS_PERMISSION]->(a)""", 
                        permGroup=permission_group, 
                        permissionName=permission
                    )

@app.post("/user")
async def add_user(user_email: str, company: str, permissionGroup:str):
    email_bool = is_valid_email(user_email)
    if not email_bool:
        raise HTTPException(status_code=400, detail="Invalid email please try again.")
    
    with driver.session() as session:
        company_check_query = """
        MATCH (c:Company {companyName: $company})
        RETURN c LIMIT 1
        """
        valid_company = session.run(company_check_query,company=company)
        if not bool(valid_company):
            raise HTTPException(status_code=400, detail="Invalid company please try again.")
    
        permission_group_check_query = """
        MATCH (p:PermissionGroup {permissionGroup: $permissionGroup}) 
        RETURN p LIMIT 1
        """
        valid_permisison_group = session.run(permission_group_check_query, permissionGroup=permissionGroup)
        if not bool(valid_permisison_group):
            raise HTTPException(status_code=400, detail="Invalid permission group please try again.")
        
        create_user_query = """
        CREATE (u:User {username: $user_name})
        WITH u
        MATCH (a:PermissionGroup {permissionGroup: $permissionGroupName})
        CREATE (u)-[:IN_PERMISSION_GROUP]->(p)
        WITH u
        MATCH (c:Company {companyName: $company})
        CREATE (u)-[:WORKS_FOR]->(c)
        """
        session.run(create_user_query,user_name=user_email, permissionGroupName=permissionGroup, company=company)

@app.put("/user/{user_email}")
async def update_user_permission(user_email:str, new_permission:str):

    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {username: $user_email})-[r:IN_PERMISSION_GROUP]->(p:PermissionGroup)
            DELETE r
            WITH u
            MATCH (p_new:PermissionGroup {permissionGroup: $new_permission})
            CREATE (u)-[:IN_PERMISSION_GROUP]->(p_new)
            """, user_email=user_email, new_permission=new_permission
        )

@app.get("/users")
async def get_users(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    with driver.session() as session:
        query = """
        MATCH (u:User)
        RETURN u.username AS username
        SKIP $skip LIMIT $limit
        """
        result = session.run(query, skip=skip, limit=limit)
        users = [dict(record) for record in result]

        return users


# if __name__ == "__main__":
uvicorn.run(app, host="0.0.0.0", port=8000)













