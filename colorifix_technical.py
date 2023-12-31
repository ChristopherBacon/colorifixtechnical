from fastapi import FastAPI, HTTPException, Query
from neo4j import GraphDatabase
import re
import uvicorn


# database access variables
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False

def build_data_model():
    with driver.session() as session:
        # create user nodes
        create_users_query = """
        UNWIND $users AS user
        MERGE (u:User {username: user.UserName})
        """
        users = [
            {"UserName": "admin@my-company.com"},
            {"UserName": "user@my-company.com"}
        ]
        session.run(create_users_query, users=users)

        # create company nodes
        create_companies_query = """
        UNWIND $companies AS company
        MERGE (c:Company {companyName: company.CompanyName})
        """
        companies = [
            {"CompanyName": "MyCompany"}
        ]
        session.run(create_companies_query, companies=companies)


        # create permission Group nodes
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

        # create relationships between permisison group and permission nodes
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

        # create relationships between users and permission groups
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


        # create relationships between users and permission groups
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


# PART 2 Create REST API
app = FastAPI()


@app.post("/company")
async def add_company(company_name: str):
    if len(company_name) == 0:
        raise HTTPException(status_code=400, detail="No company name provided please try again.")
    with driver.session() as session:
        session.run("CREATE (:Company {name: $companyName})", companyName=company_name)
    
    return {"message": f"Company: {company_name} added successfully"}

@app.post("/permission_group")
async def add_permission_group(permission_group: str, permission: str):
    if len(permission_group) == 0:
        raise HTTPException(status_code=400, detail="No permission group provided please try again.")
    if len(permission) == 0:
        raise HTTPException(status_code=400, detail="No permission provided please try again.")
    
    with driver.session() as session:
        check_permission_exists_query = """
        MATCH (a:Permission {permission: $permissionName})
        RETURN a LIMIT 1
        """
        valid_permission = session.run(check_permission_exists_query,permissionName=permission)
        if not bool(valid_permission.values()):
                raise HTTPException(status_code=400, detail="Invalid permission please try again.")
        
        create_new_permission_group_query = """
        CREATE (p:PermissionGroup {permissionGroup: $permGroup})
        WITH p
        MATCH (a:Permission {permission: $permissionName})
        CREATE (p)-[:HAS_PERMISSION]->(a)
        """
        session.run(create_new_permission_group_query, permGroup=permission_group, permissionName=permission)
        return {"message": "New Permission Group added successfully"}

@app.post("/user")
async def add_user(user_email: str, company: str, permissionGroup:str):
    email_bool = is_valid_email(user_email)
    if not email_bool:
        raise HTTPException(status_code=400, detail="Invalid email please try again.")
    
    with driver.session() as session:
        company_check_query = """
        MATCH (c:Company {companyName: $companyToCheck})
        RETURN c LIMIT 1
        """
        valid_company = session.run(company_check_query, companyToCheck=company)
        if not valid_company.single():
            raise HTTPException(status_code=400, detail="Invalid company please try again.")
    
        permission_group_check_query = """
        MATCH (p:PermissionGroup {permissionGroup: $permissionGroup}) 
        RETURN p LIMIT 1
        """
        valid_permisison_group = session.run(permission_group_check_query, permissionGroup=permissionGroup)
        if not valid_permisison_group.single():
            raise HTTPException(status_code=400, detail="Invalid permission group please try again.")
        
        create_user_query = """
        CREATE (u:User {username: $user_name})
        WITH u
        MATCH (a:PermissionGroup {permissionGroup: $permissionGroupName})
        CREATE (u)-[:IN_PERMISSION_GROUP]->(a)
        WITH u
        MATCH (c:Company {companyName: $company})
        CREATE (u)-[:WORKS_FOR]->(c)
        """
        session.run(create_user_query,user_name=user_email, permissionGroupName=permissionGroup, company=company)

        return {"message": "User created successfully"}

@app.put("/user/{user_email}")
async def update_user_permission(user_email:str, permission_group:str):

    with driver.session() as session:
        user_update_query = session.run(
            """
            MATCH (u:User {username: $user_email})
            WITH u
            OPTIONAL MATCH (u)-[r:IN_PERMISSION_GROUP]->(p:PermissionGroup)
            DELETE r
            WITH u
            MATCH (p_new:PermissionGroup {permissionGroup: $permission_group})
            CREATE (u)-[:IN_PERMISSION_GROUP]->(p_new)
            RETURN u
            """, user_email=user_email, permission_group=permission_group
        )
        if not user_update_query.single():
            raise HTTPException(status_code=404, detail="User not found or permission update failed.")
    
    return {"message": "User permission updated successfully"}

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


if __name__ == "__main__":
    
    build_data_model()
    # uvicorn.run(app, host="0.0.0.0", port=8000)