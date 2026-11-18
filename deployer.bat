@echo off
echo ============================================
echo   EduGuard - Deploiement GitHub
echo ============================================
echo.

echo [1/5] Initialisation du depot Git...
git init
git add .
git commit -m "EduGuard - Data Challenge Burkina 2026 - Defi 1 - Decrochage scolaire"

echo.
echo [2/5] IMPORTANT : Va sur https://github.com/new et cree un depot public nomme :
echo       eduguard-burkina
echo.
echo Appuie sur ENTREE une fois le depot cree sur GitHub...
pause

echo.
echo [3/5] Entre ton nom d'utilisateur GitHub :
set /p USERNAME="Username GitHub : "

echo.
echo [4/5] Connexion au depot distant...
git remote add origin https://github.com/%USERNAME%/eduguard-burkina.git
git branch -M main
git push -u origin main

echo.
echo [5/5] DEPLOIEMENT STREAMLIT CLOUD :
echo.
echo   1. Va sur : https://share.streamlit.io
echo   2. Clique "New app"
echo   3. Choisis ton depot : %USERNAME%/eduguard-burkina
echo   4. Fichier principal : eduguard_app.py
echo   5. Clique "Deploy!"
echo.
echo   Ton lien sera : https://eduguard-burkina.streamlit.app
echo.
echo ============================================
echo Deploiement termine !
echo ============================================
pause
