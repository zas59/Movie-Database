# Movie-Database
Zach Sotny

cold-shadow-9157.fly.dev 

To run locally:
- Clone over repo, all files except .env should be downloaded.
- Create a .env file
- Get an API key from themoviedb.org
- In .env file: 
    - TMDB_API_KEY = 'your-api-key-here'
    - DATABASE_URL = 'postgresql://postgres:cf50e5526041fe7d664a21b3f4243f768ccd738268a6b75c@local-host:5432'
- Uncomment last line in movie_database.py to be able to run locally.
- Save all
- Proxy the database: 
    - In a seperate terminal, run the command 'fly proxy 5432 -a cold-shadow-9157-db' and keep this running in the background.
- Run python file back in main terminal: python3 movie_database.py


2 examples where implementing your project differed from your expectations during project planning:

- One way that my project differed from my expectations was how easy using the databases was. Once I got the hang of how we set them up in the demo, it was easy to query for the reviews I wanted and use the specific parts of each review when displaying them. I was anticipating that it would be more challenging navigating the databases, but our use of them was fairly basic and provided a good intro on how to implement them.

- Another way my project differed from my expectations was how basic and not very nice looking my web app is. I thought I would have more time to focus on stylistic aspects of my web app to make it more pleasing for the viewer, but ended up having to stick with just the basics required for the project. I might try to update things on my own time to use this project on my resume since it displays a lot of useful skills. I learned a lot from doing this project and it showed me that I do have what it takes to build web apps, so I can use that now to build my own and personalize them more.

2 technical issues and how you solved them:

- One technical issue I was having was wit deployment. I had all the correct requirements and I wasn't sure what the issue could be. I looked back at the error stack trace and it was saying it couldn't connect to the database, and I realized I still had my proxy database open. I closed that and tried to deploy again, but it still wasn't working. I was even more confused now because I assumed that would have fixed the issue. I figured the next thing it could have been would be something with the database url since it was easy to mess up and it turned out I was missing the -db in my connection string. I updated it and tried to deploy again, but it would still not work. I realized I had to update my fly secrets as well, and finally I was able to deploy. If it's not one thing it's the next, it just takes persistence in finding the issue.

- Another issue I had was when I was trying to add comments on my web app. I was running locally and was running into an issue where any user who had already left a comment wasn't able to leave another one. The debugger said that it was because the keys were already being used, and I saw in my Review db Model that I had set username to be unique, so a user wasn't able to leave more than one comment. I updated my code, but the issue was still happening when I ran the app again. It was still saying that the keys had alreayd been used, and since I knew that I had fixed it in my code, I figured it had something to do with the database itself. I remembered that you have to update your tables when you change them, but I forgot how until I asked on Discord and someone helped me out. I dropped the old table and ran my app again, and the issue was solved.