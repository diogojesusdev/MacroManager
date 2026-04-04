// import type {
//   IMacroManager,
//   InvocationVariableDetails,
//   InvocationVariableName,
// } from "./types/(OLD) IMacroManager";
// import type { Folder } from "./utils/FileSystemTree";
// import os from "os";
// import { getLatestMacroLogs, getMacrosFlat } from "./utils/FileSystemUtils";
// import { exec } from "child_process";
// import path from "path";
// import fs from "fs-extra";
// import { macroTemplate } from "./utils/macro-template";
// import { macroBoilerplate } from "./utils/macro-boilerplate";

// export const MacrosPath = path.join(os.userInfo().homedir, "MacroManager");
// export const templateMacroPath = path.join(MacrosPath, "macro-template.py");
// const DEFAULT_MACRO_NAME = "macro.py";
// const PythonFrameworkName = "DesktopAutomationFramework";
// const PythonFrameworkGithubVersionFile = `https://raw.githubusercontent.com/48302-DiogoJesus/DesktopMacroFramework/main/version.txt`;

// function createEnvironment() {
//   fs.ensureDirSync(MacrosPath)

//   if (!fs.existsSync(templateMacroPath)) {
//     fs.createFileSync(templateMacroPath);
//     fs.writeFileSync(templateMacroPath, macroTemplate);
//   }
// }
// createEnvironment();

// export const MacroManager: IMacroManager = {
//   // Returns the full path of the macro
//   createMacro: function (macro_name: string): string {
//     const folderFullPath = path.join(MacrosPath, macro_name);
//     const pythonFilePath = path.join(folderFullPath, DEFAULT_MACRO_NAME);

//     // Create the macro folder
//     fs.mkdirSync(folderFullPath);

//     // Create template macro file
//     fs.writeFileSync(pythonFilePath, macroBoilerplate);

//     return pythonFilePath;
//   },

//   openMacrosFolder: () => exec(`explorer "${MacrosPath}"`),
//   openMacroInCodeEditor: (absoluteMacroPath: string) =>
//     exec(`code "${path.dirname(absoluteMacroPath)}"`),
//   openMacroInFileExplorer: (absoluteMacroPath: string) =>
//     exec(`explorer "${path.dirname(absoluteMacroPath)}"`),
//   openTaskScheduler: () => exec(`taskschd.msc`),
//   openMacroTemplate: () => {
//     createEnvironment();
//     exec(`code "${templateMacroPath}"`);
//   },

//   getMacrosFlat: () => getMacrosFlat(MacrosPath),

//   getMacrosFolderTreeLike: function (): Promise<Folder> {
//     throw new Error("Implement Later");
//   },

//   getLatestMacroLogs: getLatestMacroLogs,

//   getMacroInvocationVariablesMetadata: (absoluteMacroPath: string) => {
//     const usefulLines = fs
//       .readFileSync(absoluteMacroPath, { encoding: "utf-8" })
//       .split("\n")
//       .filter(
//         (line) =>
//           line.includes("vars.getNumber(") || line.includes("vars.getString(")
//       );

//     const invocationVariablesMetadata: {
//       [key: InvocationVariableName]: InvocationVariableDetails;
//     } = {};

//     for (const line of usefulLines) {
//       let varname: InvocationVariableName;
//       let type: InvocationVariableDetails["type"];
//       let accepted_values: InvocationVariableDetails["accepted_values"];

//       const parts = line.split("(");
//       const functionCall = parts[0].trim();
//       if (functionCall.includes("vars.getNumber")) {
//         type = "number";
//       } else if (functionCall.includes("vars.getString")) {
//         type = "string";
//       }

//       let args = parts[1].substring(1);
//       varname = args.split('"')[0];
//       args = args.replace(`${varname}"`, "");

//       let s: any = args.replace("\r", "").slice(0, -1);
//       // Has a second parameter (accepted_values)
//       if (s.charAt(0) == ",") {
//         s = s.substring(1).trim();
//         if (s.startsWith("accepted_values=")) {
//           s = s.replace("accepted_values=", "");
//         }
//         s = s.replace("[", "").replace("]", "");
//         s = s.split(",").map((item: string) => item.trim().replaceAll('"', ""));
//         accepted_values = s;
//       }
//       // Any value is accepted
//       else {
//         accepted_values = null;
//       }

//       invocationVariablesMetadata[varname] = {
//         type,
//         accepted_values,
//       };
//     }
//     return invocationVariablesMetadata;
//   },

//   runMacro: (
//     absoluteMacroPath: string,
//     invocationVariables: { [key: string]: string } = {},
//     timeBetweenInstructionsS?: string
//   ) => {
//     const keyValuePairs = Object.entries(invocationVariables)
//       .map(([key, value]) => `${key}="${value}"`)
//       .join(" ");
//     let command = `pythonw "${absoluteMacroPath}" ${keyValuePairs}`;

//     if (timeBetweenInstructionsS) {
//       command += ` --interval_s=${timeBetweenInstructionsS}`;
//     }

//     exec(command);
//   },

//   getFrameworkVersions: async function () {
//     const remoteVersion: string = await new Promise((res) => {
//       exec(`curl ${PythonFrameworkGithubVersionFile}`, (err, stdout) => {
//         res(stdout);
//       });
//     });
//     const currentVersion: string = await new Promise((res) => {
//       exec(`pip show ${PythonFrameworkName}`, (err, stdout) => {
//         const versionMatch = stdout.match(/Version: (.+)/);
//         if (versionMatch) {
//           res(versionMatch[1]);
//         }
//       });
//     });

//     return {
//       shouldUpdate: currentVersion != remoteVersion,
//       currentVersion,
//       remoteVersion,
//     };
//   },

//   shouldUpdateManager: async function () {
//     const currentVersion = await new Promise((res) => {
//       exec("git rev-parse HEAD", (err, out) =>
//         res(out.replace("HEAD", "").trim())
//       );
//     });
//     const remoteVersion = await new Promise((res) => {
//       exec("git ls-remote origin HEAD", (err, out) =>
//         res(out.replace("HEAD", "").trim())
//       );
//     });

//     return currentVersion != remoteVersion;
//   },

//   updateFramework: function (): Promise<void> {
//     return new Promise((res) => {
//       exec(
//         "pip install --upgrade --force-reinstall git+https://github.com/48302-DiogoJesus/DesktopMacroFramework",
//         (err, stdout) => {
//           console.log("updateFramework() => " + stdout);
//           res();
//         }
//       );
//     });
//   },

//   updateManager: function (): Promise<void> {
//     return new Promise((res) => {
//       exec("git pull --ff-only", (err, stdout) => {
//         console.log("updateManager() => " + stdout);
//         res();
//       });
//     });
//   },
// };
