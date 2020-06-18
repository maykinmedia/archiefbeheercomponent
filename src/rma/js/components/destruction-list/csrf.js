import React from "react";


const CsrfInput = ({csrftoken}) =>  (<input type="hidden" name="csrfmiddlewaretoken" value={csrftoken}/>);


export {CsrfInput};
