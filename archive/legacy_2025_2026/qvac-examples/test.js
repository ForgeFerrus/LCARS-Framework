import * as qvac from "@qvac/sdk";

console.log(
Object.keys(qvac)
.filter(x => x.startsWith("model"))
);