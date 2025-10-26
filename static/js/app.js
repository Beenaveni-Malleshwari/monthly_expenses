// Global chart instances
let categoryChart, monthlyChart, dailyChart;

function loadChartData() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!startDate || !endDate) {
        alert('Please select both start and end dates');
        return;
    }
    
    fetch(`/api/expense-data?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
            updateStats(data, startDate, endDate);
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
            alert('Error loading chart data. Please try again.');
        });
}

function updateCharts(data) {
    // Update category chart
    updateCategoryChart(data.category_data);
    
    // Update monthly trend chart
    updateMonthlyChart(data.monthly_data);
    
    // Update daily spending chart
    updateDailyChart(data.daily_data);
}

function updateCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    if (categoryData.labels.length === 0) {
        document.getElementById('categoryChart').style.display = 'none';
        return;
    }
    
    document.getElementById('categoryChart').style.display = 'block';
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoryData.labels,
            datasets: [{
                data: categoryData.amounts,
                backgroundColor: categoryData.colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function updateMonthlyChart(monthlyData) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    if (monthlyChart) {
        monthlyChart.destroy();
    }
    
    if (monthlyData.months.length === 0) {
        document.getElementById('monthlyChart').style.display = 'none';
        return;
    }
    
    document.getElementById('monthlyChart').style.display = 'block';
    
    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthlyData.months,
            datasets: [{
                label: 'Monthly Spending',
                data: monthlyData.amounts,
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `$${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

function updateDailyChart(dailyData) {
    const ctx = document.getElementById('dailyChart').getContext('2d');
    
    if (dailyChart) {
        dailyChart.destroy();
    }
    
    if (dailyData.dates.length === 0) {
        document.getElementById('dailyChart').style.display = 'none';
        return;
    }
    
    document.getElementById('dailyChart').style.display = 'block';
    
    dailyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dailyData.dates,
            datasets: [{
                label: 'Daily Spending',
                data: dailyData.amounts,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `$${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    ticks: {
                        maxTicksLimit: 10
                    }
                }
            }
        }
    });
}

function updateStats(data, startDate, endDate) {
    const totalSpent = data.total_spent || 0;
    const categoryCount = data.category_data.labels.length;
    const daysTracked = data.daily_data.dates.length;
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
    const avgDaily = totalSpent / (daysTracked || 1);
    
    document.getElementById('totalSpent').textContent = '$' + totalSpent.toFixed(2);
    document.getElementById('categoryCount').textContent = categoryCount;
    document.getElementById('daysTracked').textContent = daysTracked;
    document.getElementById('avgDaily').textContent = '$' + avgDaily.toFixed(2);
    
    document.getElementById('statsCards').style.display = 'flex';
}

// Utility function for number formatting
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as default for date inputs
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
});