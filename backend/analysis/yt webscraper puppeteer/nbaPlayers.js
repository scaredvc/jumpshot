const fs = require('fs');
const path = require('path');

const nbaPlayers = [];

const filePath = path.join(__dirname, 'NBA_Players.txt');

fs.readFile(filePath, 'utf8', (err, data) => {
  if (err) throw err;
  const names = data.split('\n'); // Split the data by newline character
  for (let i = 0; i < names.length; i++) {
    nbaPlayers.push(names[i].trim()); // Trim any extra whitespace
  }
  // console.log(nbaPlayers);
});

module.exports = nbaPlayers;

