# OpenSurf

Live site: https://opensurf.org

OpenSurf is an open-source surf conditions and forecasting project.  
Right now this repo contains:

- A simple landing page (GitHub Pages) at the root
- A Python CLI surf forecast tool in `cli/`
- A future browser-based app (under `webapp/`, in progress)

---

## Landing page

The root `index.html` and `style.css` power the minimal landing page currently deployed at https://opensurf.org.

To edit the copy or styles for the landing page, update those two files.

---

## CLI surf forecast tool

The CLI lives in the `cli/` directory and uses data from:

- NOAA NDBC buoy text files
- Open-Meteo marine forecast API

### Setup

```bash
git clone git@github.com:morganclemens/morganclemens.github.io.git
cd morganclemens.github.io/cli

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
