# colorifix Technical Summary
I believe I was able to complete the task roughly within the time limit. I was enjoying the task so built out a little bit beyond the time limit.
# Installation
In order to use this API to edit the neo4J database, and because the project is containerised you will need to:
  1. Ensure Docker Desktop is installed and running: (you can download here: [Get Docker Download](https://www.docker.com/get-started/)
  2. Ensure that you have a copy of neo4j desktop installed: (you can download here: [Get neo4j Desktop Download](https://neo4j.com/cloud/platform/aura-graph-database/?ref=nav-get-started-cta)
  3. Create a database and start it running, use the below credentials:
        ```python
        URI = "bolt://localhost:7687"
        USER = "neo4j"
        PASSWORD = "password"
        ```
  4. clone the repository to your local machine.
  5. Using the docker-compose.yml you should be able to right click and compose up if you are using VSCode or use the command line.
  6. ``` localhost:8000/docs``` to access the API interface
  7. ``` http://localhost:7474/browser/``` to access the neo4J database.
# Technologies Used
## neo4J
This is a new technology to me and seeing that it is used extensively at Colorifix I wanted to learn to use it for this task.
## FASTAPI
I used FastAPI as I knew it was similar to Starlite and the Starlite link was broken for me.
## Docker
I easier to  my project to make it 
