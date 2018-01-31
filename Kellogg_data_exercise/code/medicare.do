**********************************
* Mu Yang Shin
* 39 minutes
**********************************

clear

cd "\\Client\C$\hello\etc\Kellogg_data_exercise"

*********************************************************************
* 1. READ AND CLEAN RAW DATA
*********************************************************************

* read csv
import delimited "data/scp-1205.csv", numericcols(7, 8, 9, 10) clear

* set variable names
local i = 1
foreach var in countyname state contract healthplanname typeofplan countyssa eligibles enrollees penetration ABrate {
	rename v`i' `var'
	local ++i
}

* remove blanks
replace countyname = strtrim(countyname)
replace state = strtrim(state)
replace contract = strtrim(contract)
replace healthplanname = strtrim(healthplanname)
replace typeofplan = strtrim(typeofplan)
replace countyssa = strtrim(countyssa)

* missing values
replace eligibles = 0 if eligibles == .
replace enrollees = 0 if enrollees == .
replace penetration = 0 if penetration == .


*********************************************************************
* 2. CONSTRUCT A COUNTY-LEVEL DATASET
*********************************************************************

* exclude Puerto Rico and Guam
drop if state == "GU" || state == "PR"

* create new variables
sort state countyname
by state countyname: egen numberofplans1 = total(enrollees > 10)
by state countyname: egen numberofplans2 = total(penetration > 0.5)
by state countyname: egen totalenrollees = sum(enrollees)

* collapse by county
collapse (first) numberofplans1 numberofplans2 countyssa eligibles totalenrollees, by(state countyname)

* create totalpenetration
gen totalpenetration = 100 * totalenrollees / eligibles
