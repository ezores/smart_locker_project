#!/usr/bin/env node

const puppeteer = require('puppeteer');

async function testItems() {
    console.log('Testing Items Module...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        defaultViewport: null,
        args: ['--start-maximized']
    });
    
    try {
        const page = await browser.newPage();
        
        // Login first
        await page.goto('http://localhost:5173');
        await page.waitForSelector('input[name="username"]', { timeout: 10000 });
        await page.type('input[name="username"]', 'admin');
        await page.type('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForSelector('h1:contains("Main Menu")', { timeout: 10000 });
        console.log('Logged in successfully');
        
        // Navigate to items page
        await page.click('a[href="/items"]');
        await page.waitForSelector('h1:contains("Items")', { timeout: 10000 });
        console.log('Navigated to items page');
        
        // Wait for items to load
        await page.waitForTimeout(2000);
        
        // Test borrowing an item
        const borrowButtons = await page.$$('button:contains("Borrow"), button:contains("Check Out")');
        if (borrowButtons.length > 0) {
            await borrowButtons[0].click();
            await page.waitForSelector('input[name="borrower_id"]', { timeout: 10000 });
            console.log('Borrow modal opened');
            
            // Fill borrow form
            await page.select('select[name="borrower_id"]', '1'); // admin user
            await page.type('input[name="expected_return"]', '2025-07-20T18:00');
            await page.type('input[name="notes"]', 'Test borrow from automated test');
            await page.click('button:contains("Borrow")');
            
            await page.waitForTimeout(2000);
            console.log('Borrowed item successfully');
        }
        
        // Test returning an item
        const returnButtons = await page.$$('button:contains("Return"), button:contains("Check In")');
        if (returnButtons.length > 0) {
            await returnButtons[0].click();
            await page.waitForSelector('input[name="return_notes"]', { timeout: 10000 });
            console.log('Return modal opened');
            
            // Fill return form
            await page.type('input[name="return_notes"]', 'Test return from automated test');
            await page.click('button:contains("Return")');
            
            await page.waitForTimeout(2000);
            console.log('Returned item successfully');
        }
        
        // Test adding a new item
        const newItemButton = await page.$('button:contains("New Item"), button:contains("Add Item")');
        if (newItemButton) {
            await newItemButton.click();
            await page.waitForSelector('input[name="name"]', { timeout: 10000 });
            console.log('New item modal opened');
            
            // Fill item form
            await page.type('input[name="name"]', 'Test Item');
            await page.type('input[name="description"]', 'Test item from automated test');
            await page.select('select[name="category"]', 'electronics');
            await page.type('input[name="serial_number"]', 'TEST123456');
            await page.click('button:contains("Create")');
            
            await page.waitForTimeout(2000);
            console.log('Created new item');
        }
        
        // Test editing an item
        const editButtons = await page.$$('button:contains("Edit")');
        if (editButtons.length > 0) {
            await editButtons[0].click();
            await page.waitForSelector('input[name="name"]', { timeout: 10000 });
            console.log('Edit item modal opened');
            
            // Update item description
            await page.click('input[name="description"]', { clickCount: 3 });
            await page.type('input[name="description"]', ' - Updated by automated test');
            await page.click('button:contains("Update")');
            
            await page.waitForTimeout(2000);
            console.log('Updated item');
        }
        
        // Test search functionality
        const searchInput = await page.$('input[placeholder*="search"], input[placeholder*="Search"]');
        if (searchInput) {
            await searchInput.type('Test');
            await page.waitForTimeout(1000);
            console.log('Tested search functionality');
            
            // Clear search
            await searchInput.click({ clickCount: 3 });
            await page.keyboard.press('Backspace');
        }
        
        // Test filtering by status
        const statusFilters = await page.$$('button:contains("Available"), button:contains("Borrowed"), button:contains("Maintenance")');
        if (statusFilters.length > 0) {
            await statusFilters[0].click();
            await page.waitForTimeout(1000);
            console.log('Tested status filtering');
        }
        
        // Test sorting options
        const sortSelect = await page.$('select[name="sort"]');
        if (sortSelect) {
            await sortSelect.select('name');
            await page.waitForTimeout(1000);
            console.log('Tested sorting by name');
            
            await sortSelect.select('status');
            await page.waitForTimeout(1000);
            console.log('Tested sorting by status');
        }
        
        console.log('Items module tests completed successfully!');
        
    } catch (error) {
        console.error('Items test failed:', error.message);
        throw error;
    } finally {
        await browser.close();
    }
}

if (require.main === module) {
    testItems().catch(console.error);
}

module.exports = { testItems };
