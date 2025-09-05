// Krishi Sahayak - Farm Assistant Application

// Application data
const appData = {
  farmer: {
    name: "राम कुमार",
    location: "गाजीपुर, उत्तर प्रदेश",
    phone: "+91-9876543210",
    landSize: "5 एकड़"
  },
  crops: [
    {
      id: 1,
      name: "धान",
      plantDate: "2024-07-15",
      harvestDate: "2024-11-15",
      fieldSize: "2 एकड़",
      stage: "फूल आना",
      progress: 65,
      nextAction: "कीटनाशक छिड़काव",
      daysToHarvest: 45
    },
    {
      id: 2,
      name: "गेहूं",
      plantDate: "2024-11-20",
      harvestDate: "2025-04-15",
      fieldSize: "3 एकड़", 
      stage: "बुआई की तैयारी",
      progress: 10,
      nextAction: "खेत की तैयारी",
      daysToHarvest: 145
    }
  ],
  weather: {
    current: {
      temperature: "28°C",
      humidity: "65%",
      rainfall: "0 मिमी",
      condition: "आंशिक बादल",
      windSpeed: "12 किमी/घंटा"
    },
    forecast: [
      {"day": "आज", "high": "30°C", "low": "22°C", "condition": "धूप", "rain": "0%"},
      {"day": "कल", "high": "32°C", "low": "24°C", "condition": "धूप", "rain": "10%"},
      {"day": "परसों", "high": "29°C", "low": "21°C", "condition": "बारिश", "rain": "80%"},
      {"day": "बुधवार", "high": "26°C", "low": "20°C", "condition": "बादल", "rain": "60%"},
      {"day": "बृहस्पति", "high": "28°C", "low": "22°C", "condition": "धूप", "rain": "20%"}
    ]
  },
  marketPrices: [
    {"crop": "धान", "price": "₹2,150/क्विंटल", "change": "+5%", "market": "गाजीपुर मंडी"},
    {"crop": "गेहूं", "price": "₹2,250/क्विंटल", "change": "+2%", "market": "वाराणसी मंडी"},
    {"crop": "आलू", "price": "₹1,200/क्विंटल", "change": "-3%", "market": "आगरा मंडी"},
    {"crop": "प्याज", "price": "₹3,500/क्विंटल", "change": "+15%", "market": "नासिक मंडी"},
    {"crop": "टमाटर", "price": "₹2,800/क्विंटल", "change": "+8%", "market": "दिल्ली मंडी"}
  ]
};

// Global variables
let priceChart;
let currentSection = 'dashboard';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

function initializeApp() {
  // Set current date
  setCurrentDate();
  
  // Create overlay for mobile
  createOverlay();
  
  // Populate initial data
  populateCropsList();
  populateMarketPrices();
  initializePriceChart();
  
  // Set up event listeners
  setupEventListeners();
  
  // Show dashboard by default
  showSection('dashboard');
  
  console.log('कृषि सहायक ऐप लोड हो गया');
}

function setCurrentDate() {
  const now = new Date();
  const options = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
  };
  const dateStr = now.toLocaleDateString('hi-IN', options);
  
  const currentDateElement = document.getElementById('currentDate');
  if (currentDateElement) {
    currentDateElement.textContent = dateStr;
  }
}

function createOverlay() {
  // Create overlay element for mobile sidebar
  const existingOverlay = document.querySelector('.mobile-overlay');
  if (!existingOverlay) {
    const overlay = document.createElement('div');
    overlay.className = 'mobile-overlay';
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      z-index: 150;
      display: none;
    `;
    document.body.appendChild(overlay);
    
    // Add click listener to close sidebar
    overlay.addEventListener('click', function() {
      closeSidebar();
    });
  }
}

function setupEventListeners() {
  // Window resize handler
  window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
      closeSidebar();
    }
  });
  
  // Ensure menu toggle button works
  const menuToggle = document.querySelector('.header__menu-toggle');
  if (menuToggle) {
    menuToggle.addEventListener('click', function(e) {
      e.preventDefault();
      toggleSidebar();
    });
  }
}

// Navigation functions
function showSection(sectionId) {
  // Hide all sections
  const sections = document.querySelectorAll('.section');
  sections.forEach(section => section.classList.remove('active'));
  
  // Show selected section
  const targetSection = document.getElementById(sectionId);
  if (targetSection) {
    targetSection.classList.add('active');
  }
  
  // Update sidebar active state
  const sidebarLinks = document.querySelectorAll('.sidebar__link');
  sidebarLinks.forEach(link => link.classList.remove('active'));
  
  const activeLink = document.querySelector(`[onclick="showSection('${sectionId}')"]`);
  if (activeLink) {
    activeLink.classList.add('active');
  }
  
  currentSection = sectionId;
  
  // Close sidebar on mobile after navigation
  if (window.innerWidth <= 768) {
    closeSidebar();
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  
  if (sidebar.classList.contains('open')) {
    closeSidebar();
  } else {
    openSidebar();
  }
}

function openSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.querySelector('.mobile-overlay');
  
  if (sidebar) {
    sidebar.classList.add('open');
  }
  
  if (overlay) {
    overlay.style.display = 'block';
  }
  
  // Prevent body scroll
  document.body.style.overflow = 'hidden';
}

function closeSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.querySelector('.mobile-overlay');
  
  if (sidebar) {
    sidebar.classList.remove('open');
  }
  
  if (overlay) {
    overlay.style.display = 'none';
  }
  
  // Restore body scroll
  document.body.style.overflow = '';
}

// Crop management functions
function populateCropsList() {
  const cropsList = document.getElementById('cropsList');
  if (!cropsList) return;
  
  cropsList.innerHTML = '';
  
  appData.crops.forEach(crop => {
    const cropCard = createCropCard(crop);
    cropsList.appendChild(cropCard);
  });
}

function createCropCard(crop) {
  const card = document.createElement('div');
  card.className = 'crop-card';
  
  const statusClass = getStatusClass(crop.stage);
  
  card.innerHTML = `
    <div class="crop-card__header">
      <h4>${getCropIcon(crop.name)} ${crop.name}</h4>
      <span class="status ${statusClass}">${crop.stage}</span>
    </div>
    <div class="crop-progress">
      <div class="progress-bar">
        <div class="progress-bar__fill" style="width: ${crop.progress}%"></div>
      </div>
      <span>${crop.progress}% पूर्ण</span>
    </div>
    <p class="crop-action">अगला कार्य: ${crop.nextAction}</p>
    <div style="margin-top: 12px; font-size: 12px; color: var(--color-text-secondary);">
      <div>क्षेत्रफल: ${crop.fieldSize}</div>
      <div>कटाई तक: ${crop.daysToHarvest} दिन</div>
    </div>
  `;
  
  return card;
}

function getCropIcon(cropName) {
  const icons = {
    'धान': '🌾',
    'गेहूं': '🌾',
    'मक्का': '🌽',
    'बाजरा': '🌾',
    'आलू': '🥔',
    'टमाटर': '🍅',
    'प्याज': '🧅'
  };
  return icons[cropName] || '🌱';
}

function getStatusClass(stage) {
  const statusClasses = {
    'बुआई की तैयारी': 'status--info',
    'अंकुरण': 'status--info',
    'वृद्धि': 'status--warning',
    'फूल आना': 'status--warning',
    'फल बनना': 'status--success',
    'पकना': 'status--success'
  };
  return statusClasses[stage] || 'status--info';
}

function showAddCropForm() {
  const form = document.getElementById('addCropForm');
  if (form) {
    form.classList.remove('hidden');
    // Scroll to form
    form.scrollIntoView({ behavior: 'smooth' });
  }
}

function hideAddCropForm() {
  const form = document.getElementById('addCropForm');
  if (form) {
    form.classList.add('hidden');
    // Reset form
    const formElement = form.querySelector('form');
    if (formElement) {
      formElement.reset();
    }
  }
}

function addNewCrop(event) {
  event.preventDefault();
  
  const newCrop = {
    id: appData.crops.length + 1,
    name: document.getElementById('cropName').value,
    plantDate: document.getElementById('plantDate').value,
    harvestDate: document.getElementById('harvestDate').value,
    fieldSize: document.getElementById('fieldSize').value + ' एकड़',
    stage: document.getElementById('cropStage').value,
    progress: 15, // Initial progress
    nextAction: getNextActionForStage(document.getElementById('cropStage').value),
    daysToHarvest: calculateDaysToHarvest(document.getElementById('harvestDate').value)
  };
  
  // Add to data
  appData.crops.push(newCrop);
  
  // Refresh UI
  populateCropsList();
  hideAddCropForm();
  
  // Show success message
  showNotification('नई फसल सफलतापूर्वक जोड़ी गई!', 'success');
}

function getNextActionForStage(stage) {
  const actions = {
    'बुआई की तैयारी': 'खेत की तैयारी',
    'अंकुरण': 'पानी देना',
    'वृद्धि': 'उर्वरक डालना',
    'फूल आना': 'कीटनाशक छिड़काव',
    'फल बनना': 'सिंचाई करना',
    'पकना': 'कटाई की तैयारी'
  };
  return actions[stage] || 'देखभाल';
}

function calculateDaysToHarvest(harvestDate) {
  const harvest = new Date(harvestDate);
  const today = new Date();
  const diffTime = harvest - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return Math.max(0, diffDays);
}

// Market prices functions
function populateMarketPrices() {
  const pricesTable = document.getElementById('pricesTable');
  if (!pricesTable) return;
  
  pricesTable.innerHTML = '';
  
  appData.marketPrices.forEach(item => {
    const row = document.createElement('tr');
    
    const changeClass = item.change.startsWith('+') ? 'positive' : 'negative';
    
    row.innerHTML = `
      <td>${getCropIcon(item.crop)} ${item.crop}</td>
      <td><strong>${item.price}</strong></td>
      <td><span class="price-change ${changeClass}">${item.change}</span></td>
      <td>${item.market}</td>
    `;
    
    pricesTable.appendChild(row);
  });
}

function refreshPrices() {
  // Simulate price updates
  appData.marketPrices.forEach(item => {
    const randomChange = (Math.random() - 0.5) * 10;
    const sign = randomChange > 0 ? '+' : '';
    item.change = sign + Math.round(randomChange) + '%';
  });
  
  populateMarketPrices();
  showNotification('बाजार भाव अपडेट किया गया', 'success');
}

// Price chart initialization
function initializePriceChart() {
  const ctx = document.getElementById('priceChart');
  if (!ctx) return;
  
  const chartData = {
    labels: ['धान', 'गेहूं', 'आलू', 'प्याज', 'टमाटर'],
    datasets: [{
      label: 'भाव (₹/क्विंटल)',
      data: [2150, 2250, 1200, 3500, 2800],
      backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F'],
      borderColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F'],
      borderWidth: 2
    }]
  };
  
  priceChart = new Chart(ctx, {
    type: 'bar',
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '₹' + value;
            }
          }
        }
      }
    }
  });
}

// FAQ functions
function toggleFAQ(element) {
  const faqItem = element.parentElement;
  const answer = faqItem.querySelector('.faq-answer');
  
  if (answer.style.display === 'block') {
    answer.style.display = 'none';
  } else {
    // Close all other FAQs
    const allAnswers = document.querySelectorAll('.faq-answer');
    allAnswers.forEach(ans => ans.style.display = 'none');
    
    // Open this one
    answer.style.display = 'block';
  }
}

function submitQuestion(event) {
  event.preventDefault();
  
  const question = event.target.querySelector('textarea').value;
  const crop = event.target.querySelector('input').value;
  
  if (question.trim()) {
    showNotification('आपका प्रश्न विशेषज्ञ को भेजा गया है। जल्द ही जवाब मिलेगा।', 'success');
    event.target.reset();
  }
}

// Records functions
function showRecordTab(tabName) {
  // Hide all record contents
  const contents = document.querySelectorAll('.record-content');
  contents.forEach(content => content.classList.remove('active'));
  
  // Show selected content
  const targetContent = document.getElementById(tabName);
  if (targetContent) {
    targetContent.classList.add('active');
  }
  
  // Update tab buttons
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(tab => tab.classList.remove('active'));
  
  // Find and activate the clicked tab
  const clickedTab = event?.target;
  if (clickedTab) {
    clickedTab.classList.add('active');
  }
}

function addNewRecord() {
  showNotification('नया रिकॉर्ड जोड़ने की सुविधा जल्द आएगी', 'info');
}

// Notification system
function showNotification(message, type = 'info') {
  const notifications = document.getElementById('notifications');
  if (!notifications) return;
  
  const notification = document.createElement('div');
  notification.className = `notification notification--${type}`;
  notification.textContent = message;
  
  notifications.appendChild(notification);
  
  // Auto remove after 3 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 3000);
}

// Search and filter functions (for future enhancement)
function searchCrops(query) {
  // Implementation for crop search
  console.log('खोज रहे हैं:', query);
}

function filterMarketPrices(criteria) {
  // Implementation for price filtering
  console.log('फिल्टर कर रहे हैं:', criteria);
}

// Data validation helpers
function validateCropForm(formData) {
  const required = ['cropName', 'plantDate', 'harvestDate', 'fieldSize'];
  
  for (let field of required) {
    if (!formData.get(field)) {
      showNotification(`${field} आवश्यक है`, 'error');
      return false;
    }
  }
  
  return true;
}

// Weather helpers
function getWeatherIcon(condition) {
  const icons = {
    'धूप': '☀️',
    'बादल': '☁️',
    'आंशिक बादल': '⛅',
    'बारिश': '🌧️',
    'तूफान': '⛈️'
  };
  return icons[condition] || '🌤️';
}

// Export functions for global access
window.showSection = showSection;
window.toggleSidebar = toggleSidebar;
window.showAddCropForm = showAddCropForm;
window.hideAddCropForm = hideAddCropForm;
window.addNewCrop = addNewCrop;
window.refreshPrices = refreshPrices;
window.toggleFAQ = toggleFAQ;
window.submitQuestion = submitQuestion;
window.showRecordTab = showRecordTab;
window.addNewRecord = addNewRecord;

console.log('🌾 कृषि सहायक ऐप तैयार है!');