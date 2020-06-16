import React from "react";


function CsrfInput(props) {
    const {csrftoken} = props;

    return <input type="hidden" name="csrfmiddlewaretoken" value={csrftoken}/>;
}


export {CsrfInput};
