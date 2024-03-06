// var responseString = "{'index':[['zs_000001']],'date':[['2022-01-01','2022-01-02']]}";

// var jsonData = eval("(" + responseString + ")");
// console.log(jsonData);




const https = require('https');
const iconv = require('iconv-lite');

const url = 'https://hq.stock.sohu.com/zs/001/zs_000001-1.html?_=1709176367598';
const substring = 'fortune_hq';

https.get(url, (res) => {
  res.setEncoding('binary'); // 设置编码为binary

  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    const utf8Data = iconv.decode(Buffer.from(data, 'binary'), 'gbk'); // 将gbk编码转换为utf-8编码
    console.log(utf8Data);
  });
});








