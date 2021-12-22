import './api';

const jsonScriptToVar = (id) => {
    const node = document.getElementById(id);
    return JSON.parse(node.text);
};


const countObjectKeys = (obj) => {
    return Object.keys(obj).reduce(
        (acc, key) => obj[key] ? acc + 1 : acc,
    0);
};

const getObjectKeys = (obj) => {
    return Object.keys(obj).filter(
        (key, index) => obj[key]
    );
};


export { jsonScriptToVar, countObjectKeys, getObjectKeys };
