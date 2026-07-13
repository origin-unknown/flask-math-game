# Flask Math Game

A prototype of a turn-based math game for learning multiplication, based on chat rooms and written in Flask and Svelte 5.

## Install the dependencies and run or build the frontend
```bash
cd frontend 
npm install
npm run dev
# or 
npm run build 
```

## Install the dependencies and run the backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/app.py
```

The example is designed so that the Svelte application can be served via the Flask server when the `npm run build` command is finally executed. However, it can also be accessed during the development process via the two separately running servers of Flask and Svelte.