import React from "react";

const ConstantsContext = React.createContext({
    prefix: "formset",
    zaakDetailUrl: "",
});

const SuggestionContext = React.createContext({
    suggestions: [],
    setSuggestions: undefined,
});

export { ConstantsContext, SuggestionContext };
