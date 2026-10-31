# Flask Math Game

A prototype of a turn-based math game, built using Flask and Svelte 5 and structured around chatrooms. LaTeX is used to display problems that multiple users can solve while competing against one another.

> [!IMPORTANT]
> This project is proprietary. All rights are reserved by origin-unknown. 
> You may view and review the code for educational purposes, but copying, modification, or redistribution is strictly prohibited. See the [LICENSE](LICENSE.md) file for details.

## Requirements 
- [Python](https://www.python.org/)
- [NodeJS](https://nodejs.org/)

## Install the dependencies and run the backend (Linux/MacOS)
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

## Install the dependencies and run or build the frontend
```bash
cd frontend 
npm install

# Start the frontend server and open the page in the browser, 
npm run dev -- --open

# or build the frontend and export it to the backend server. 
# In this case, the frontend will be served via the backend server. 
# The frontend server is not required. However, the frontend will 
# not update automatically when the code is changed.
# 
# npm run build
```

The example is designed so that the Svelte application can be served via the Flask server when the `npm run build` command is finally executed. However, it can also be accessed during the development process via the two separately running servers of Flask and Svelte.