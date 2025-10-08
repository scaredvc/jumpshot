const puppeteer = require('puppeteer-extra')
const fs = require('fs')
const nbaPlayers = require('./nbaPlayers');


// add stealth plugin and use defaults (all evasion techniques)
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin())

let count = 0;

const ytSearch = async (page, searchQuery) => {
    const encodedQuery = encodeURIComponent(searchQuery);
  const url = `https://www.youtube.com/results?search_query=${encodedQuery}`;
  await page.goto(url);
  const sel = "a#video-title";
  await page.waitForSelector(sel);
  return page.$$eval(sel, els =>
    els.map(e => ({
      href: e.href,
    }))
  );

  // Check each video for subtitles
  for (const link of videoLinks) {
    const hasSubtitles = await hasCC(page, link);
    if (hasSubtitles) {
        return link; // Return the first video with subtitles
    }
  }
  return null; // Return null if no subtitles found

};

const summarizeAnalysis = async (page, link) => {
    console.log('running analysis...')
    await page.goto('https://www.summarize.tech', {waitUntil: 'load'});
    const inputBarSelector = 'input[placeholder="URL of a YouTube video"]'
    await page.waitForSelector(inputBarSelector);
    await page.type(inputBarSelector, link)
    await page.keyboard.press('Enter')
    await page.waitForNavigation({waitUntil: 'load'})
    
    const grabParagraph = await page.evaluate(() =>{
        const paragraphTag = document.querySelector(".d-none");
        return paragraphTag.innerText;
    });
    return(grabParagraph)
}

function linkfilter(links) {
    return links.find(link => link.includes('/watch'))
    
}

const hasCC = async (page, videoUrl) => {
  await page.goto(videoUrl, {waitUntil: 'networkidle2'});

  // Try to detect closed captions by checking for the presence of captions-related elements
  const ccAvailable = await page.evaluate(() => {
      const captionsButton = document.querySelector('.ytp-subtitles-button'); // YouTube's CC button
      return captionsButton !== null;
  });

  return ccAvailable;
};

// Export the analysis function so it can be called from Python
module.exports = async function getPlayerAnalysis(playerName) {
  const browser = await puppeteer.launch({ headless: true }); // Changed to headless: true for production
  try {
    const page = await browser.newPage();
    const results = await ytSearch(page, `${playerName} basketball shooting form full breakdown`);
    let urls = results.map(item => item.href);
    let ytVideoLink = linkfilter(urls);
    const analysisParagraph = await summarizeAnalysis(page, ytVideoLink);
    return analysisParagraph;
  } finally {
    await browser.close();
  }
}