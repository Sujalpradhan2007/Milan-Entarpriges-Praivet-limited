# Enterprise Machine Portal

Advanced Flask + SQLite website for an industrial machine company.

## Included
- Public corporate website
- Machine catalog with search/filter
- Machine details with photo/video, price, offers, colors, raw materials, specifications
- Performance comparison (Speed / Accuracy / Efficiency)
- Admin login and dashboard
- Add/edit/delete machines
- Machine photo and video uploads
- Raw-material management with image uploads
- Editable FAQs
- Animated festival/offer banner management
- Customer inquiry database
- Direct WhatsApp inquiry buttons (configured for 7978266937)
- Responsive mobile-friendly design

## Run on Windows
1. Install Python 3.11+.
2. Open PowerShell in this folder.
3. `python -m venv venv`
4. `venv\\Scripts\\activate`
5. `pip install -r requirements.txt`
6. Set `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `SECRET_KEY` in your environment.
7. `python app.py`
8. Open http://127.0.0.1:5000

## Admin
Open `/admin` on your deployed site. The admin account is created only when both `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables are configured. Never commit these values to GitHub.

Set these environment variables in your hosting provider:
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `SECRET_KEY`
- `PORT` (provided automatically by most hosts)
