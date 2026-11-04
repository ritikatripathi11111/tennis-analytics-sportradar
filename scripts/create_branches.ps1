# Run from the project root after extracting the ZIP.
git init
git add .
git commit -m "chore: initialize tennis analytics project"
git branch -M main
git switch -c development
git switch -c feature/api-integration
git switch development
git switch -c feature/database-sql
git switch development
git switch -c feature/streamlit-dashboard
git switch development
git switch -c feature/integration-testing
git switch main
Write-Host "Local branches created. Create an empty GitHub repository, add its URL as origin, then push all branches."
