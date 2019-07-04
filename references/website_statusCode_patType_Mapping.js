// this snippet is from patent-overview.js on that website
var _temp = Number(this.patType);
if (_temp === 1) {
    this.patClass = "pat-label pat-yellow";
    if (this.dbName === 'FMZL') {
        this.patTypeLabel = '发明公开';
    } else {
        this.patTypeLabel = '发明授权';
    }
} else if (_temp  === 2) {
    this.patClass = "pat-label pat-blue";
    this.patTypeLabel = '实用新型';
} else if (_temp  === 3) {
    this.patClass = "pat-label pat-skyblue";
    this.patTypeLabel = '外观专利';
} else if (_temp  === 8) {
    this.patClass ="pat-label pat-green";
    if (this.dbName === 'FMZL') {
        this.patTypeLabel = '发明公开';
    } else {
        this.patTypeLabel = '发明授权';
    }
} else if (_temp  === 9) {
    this.patClass ="pat-label pat-blue";
    this.patTypeLabel = '实用新型';
}
_temp = Number(this.statusCode);
if (_temp === 10) {
    this.legalClass = "pat-label pat-green";
    this.legalStatusLabel = '有效专利';
} else if (_temp === 20) {
    this.legalClass = "pat-label pat-red";
    this.legalStatusLabel = '失效专利';
} else if (_temp === 21) {
    this.legalClass = "pat-label pat-blue";
    this.legalStatusLabel = '专利权届满的专利';
} else if (_temp === 22) {
    this.legalClass = "pat-label pat-skyblue";
    this.legalStatusLabel = '在审超期';
} else if (_temp === 30) {
    this.legalClass = "pat-label pat-yellow";
    this.legalStatusLabel = '在审专利';
} else {
    this.legalClass = "pat-label pat-grey";
    this.legalStatusLabel = '';
}
