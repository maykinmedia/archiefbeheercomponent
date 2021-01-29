import React from "react";


const ActionIcon = ({action}) => {
    const icon = (action === "remove" ? "clear": (action === "change_and_remove" ? "create" : "done"));

    return <i className="material-icons">{icon}</i>;
};


export {ActionIcon};
