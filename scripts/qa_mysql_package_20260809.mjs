import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

const root=path.resolve(".");
const files=[
  "sql/01_create_english_dataset.sql",
  "sql/02_load_english_dataset.sql",
  "sql/03_validate_english_dataset.sql",
  "sql/04_analysis_queries.sql",
  "docs/mysql_english_dataset_import.md"
];
const expected=["person_id","source_position_id","district","settlement","person_seq","household_id","household_type","legal_status","full_name","sex","family_status","age","age_months","religion","origin_place","arrival_year","occupation","literacy","marital_status","living_alone_status","allowance_status","illness","archive_code"];
const text=Object.fromEntries(await Promise.all(files.map(async f=>[f,await fs.readFile(path.join(root,f),"utf8")])));
const schemaBlock=text[files[0]].match(/CREATE TABLE[\s\S]*?\n\)/)?.[0]??"";
const schemaColumns=[...schemaBlock.matchAll(/^\s{4}([a-z][a-z0-9_]*)\s+(?:CHAR|VARCHAR|SMALLINT|TINYINT|BOOLEAN)/gm)].map(m=>m[1]);
const checks=[
  ["schema_column_order",JSON.stringify(schemaColumns)===JSON.stringify(expected)],
  ["utf8mb4",/CHARACTER SET utf8mb4/.test(text[files[0]])],
  ["primary_key",/PRIMARY KEY \(person_id\)/.test(text[files[0]])],
  ["source_position_unique",/UNIQUE KEY[^\n]+\(source_position_id\)/.test(text[files[0]])],
  ["load_local_infile",/LOAD DATA LOCAL INFILE/.test(text[files[1]])],
  ["csv_header_ignored",/IGNORE 1 LINES/.test(text[files[1]])],
  ["nullable_blank_conversion",(text[files[1]].match(/NULLIF\(/g)??[]).length>=14],
  ["boolean_conversion",/WHEN @allowance_status = 'TRUE' THEN 1[\s\S]*WHEN @allowance_status = 'FALSE' THEN 0/.test(text[files[1]])],
  ["record_validation",/COUNT\(\*\) = 7446/.test(text[files[2]])],
  ["cyrillic_validation",/REGEXP '\[А-Яа-яЁё\]'/.test(text[files[2]])],
  ["analysis_queries",(text[files[3]].match(/SELECT /g)??[]).length>=8],
  ["import_documented",/local_infile=ON/.test(text[files[4]])]
];
const hashes=[];for(const f of files){const b=await fs.readFile(path.join(root,f));hashes.push({file:f,bytes:b.length,sha256:crypto.createHash("sha256").update(b).digest("hex")});}
const report={status:checks.every(c=>c[1])?"PASS":"FAIL",date:"2026-08-09",mysql_runtime_available:true,mysql_service:"MySQL80",mysql_service_status:"Running",mysql_client:"C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe",actual_server_load_performed:false,server_test_pending_reason:"Authenticated database connection not supplied to the automated workspace session",expected_columns:expected,schema_columns:schemaColumns,checks:Object.fromEntries(checks.map(([k,v])=>[k,v?"PASS":"FAIL"])),hashes};
const out=path.join(root,"outputs/qa/mysql_package_20260809");await fs.mkdir(out,{recursive:true});await fs.writeFile(path.join(out,"mysql_package_static_qa_20260809.json"),JSON.stringify(report,null,2)+"\n","utf8");console.log(JSON.stringify(report));if(report.status!=="PASS")process.exitCode=1;
