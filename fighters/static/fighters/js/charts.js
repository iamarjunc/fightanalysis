/* fighters/static/fighters/js/charts.js */
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.animate-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    const titles = document.querySelectorAll('.animate-title');
    titles.forEach((title, index) => {
        title.style.animationDelay = `${index * 0.2}s`;
    });
    const photos = document.querySelectorAll('.animate-photo');
    photos.forEach((photo, index) => {
        photo.style.animationDelay = `${index * 0.3}s`;
    });
    const charts = document.querySelectorAll('.animate-chart');
    charts.forEach((chart, index) => {
        chart.style.animationDelay = `${index * 0.4}s`;
    });
});