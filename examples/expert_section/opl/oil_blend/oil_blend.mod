/*********************************************
 * OPL oil_blend problem organized into tabular, ticdat compliant format
 * See https://goo.gl/kqXmQE for reference problem and sample data.
 *********************************************/

/* creates inp_oil, inp_gas, inp_parameters
include "ticdat_oil_blend.mod";

/* use the inp_ data to populate the original data structures */

{string} Gasolines = {n | <n,d,s,o,l> in inp_gas};
{string} Oils = {n | <n,s,p,o,l> in inp_oil};
tuple gasType {
  float demand;
  float price;
  float octane;
  float lead;
}

tuple oilType {
  float capacity;
  float price;
  float octane;
  float lead;
}

/* PJC-JOSH next 2 lines are probably wrong - please review */
gasType Gas[Gasolines] = [n: <d,s,o,l> |  <n,d,s,o,l> in inp_gas];
oilType Oil[Oils] = [n: <s,p,o,l> | <n,s,p,o,l> in inp_oil];
/* PJC-JOSH - really flailing next 2 lines - just trying to get parameter value or zero if missing
float MaxProduction = sum(v for <k,v> in inp_parameters if k == "Maximum Production");
float ProdCost = sum(v for <k,v> in inp_parameters if k == "Production Cost");

/* begin block of code that's exactly the same as https://goo.gl/kqXmQE */
dvar float+ a[Gasolines];
dvar float+ Blend[Oils][Gasolines];


maximize
  sum( g in Gasolines , o in Oils )
    (Gas[g].price - Oil[o].price - ProdCost) * Blend[o][g]
    - sum(g in Gasolines) a[g];
subject to {
  forall( g in Gasolines )
    ctDemand:
      sum( o in Oils )
        Blend[o][g] == Gas[g].demand + 10*a[g];
  forall( o in Oils )
    ctCapacity:
      sum( g in Gasolines )
        Blend[o][g] <= Oil[o].capacity;
  ctMaxProd:
    sum( o in Oils , g in Gasolines )
      Blend[o][g] <= MaxProduction;
  forall( g in Gasolines )
    ctOctane:
      sum( o in Oils )
        (Oil[o].octane - Gas[g].octane) * Blend[o][g] >= 0;
  forall( g in Gasolines )
    ctLead:
      sum( o in Oils )
        (Oil[o].lead - Gas[g].lead) * Blend[o][g] <= 0;
}

execute DISPLAY_REDUCED_COSTS{
  for( var g in Gasolines ) {
    writeln("a[",g,"].reducedCost = ",a[g].reducedCost);
  }
}
/* end block of code that's exactly the same as https://goo.gl/kqXmQE */

/* write out solution */
include "ticdat_oil_blend_output.mod";
float total_advertising = sum(g in Gasolines) a[g];
float total_purchase_cost = sum( g in Gasolines , o in Oils ) Oil[o].price * Blend[o][g]
float total_production_cost = sum( g in Gasolines , o in Oils ) ProdCost * Blend[o][g]
float total_revenue = sum( g in Gasolines , o in Oils ) Gas[g].price * Blend[o][g]
execute {
   for (var o in Oils){
        for (var g in Gasolines){
            sln_blending.add(o,g,Blend[o][g])
        }
   }
   for (var g in Gasolines){
        sln_advertising.add(g,a[g])
   }
   parameters.add("Total Advertising Spend",total_advertising);
   parameters.add("Total Oil Purchase Cost",total_purchase_cost);
   parameters.add("Total Production Cost",total_production_cost);
   parameters.add("Total Revenue",total_revenue);
   parameters.add("Total Profit",total_revenue - total_advertising - total_purchase_cost - total_production_cost);
}