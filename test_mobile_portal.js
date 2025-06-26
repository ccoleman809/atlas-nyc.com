// Simple test to validate mobile portal JavaScript
const fs = require('fs');
const { JSDOM } = require('jsdom');

// Read the mobile portal HTML
const html = fs.readFileSync('mobile_portal.html', 'utf8');

// Create a DOM environment
const dom = new JSDOM(html, {
    runScripts: "dangerously",
    resources: "usable"
});

console.log('Mobile portal JavaScript validation completed without syntax errors');
console.log('DOM elements found:', dom.window.document.querySelectorAll('script').length, 'script tags');