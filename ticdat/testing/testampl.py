import os
import sys
from ticdat.ticdatfactory import TicDatFactory, amplpy
import ticdat.utils as utils
from ticdat.testing.ticdattestutils import nearlySame, fail_to_debugger
import unittest

def _nearly_same_dat(tdf, dat1, dat2):
    def _same_table(t1, t2):
        if not set(t1) == set(t2):
            return False
        for k in t1:
            for f in t1[k]:
                if not nearlySame(t1[k][f], t2[k][f]):
                    return False
        return True
    return all(_same_table(getattr(dat1, t), getattr(dat2, t)) for t in tdf.all_tables)

# using the diet/netlfow flavors consistent with the examples instead of the older ones in
# ticdat.testing.ticdattestutils

# the diet_mod is hacked from the example code to get exercise more amplpy behaviors
_diet_mod = """
    set CAT;
    set FOOD;

    param cost {FOOD};

    param n_min {CAT} >= 0;
    param n_max {i in CAT} >= n_min[i];

    param amt {FOOD, CAT} >= 0;
    param other_amt {FOOD, CAT} >= 0;

    var Buy {j in FOOD} >= 0;
    var Consume {i in CAT } >= n_min [i], <= n_max [i];

    minimize Total_Cost:  sum {j in FOOD} cost[j] * Buy[j];

    subject to Diet {i in CAT}:
       Consume[i] =  sum {j in FOOD} (amt[j,i] + other_amt[j,i]) * Buy[j];
    """
_diet_input_tdf = TicDatFactory (
    categories = [["Name"],["Min Nutrition", "Max Nutrition"]],
    foods  = [["Name"],["Cost"]],
    nutrition_quantities = [["Food", "Category"], ["Quantity", "Other Quantity"]])
_diet_dat = _diet_input_tdf.TicDat(**{'categories': {
  u'calories': {'Max Nutrition': 2200.0, 'Min Nutrition': 1800},
  u'fat': {'Max Nutrition': 65.0, 'Min Nutrition': 0},
  u'protein': {'Max Nutrition': float('inf'), 'Min Nutrition': 91},
  u'sodium': {'Max Nutrition': 1779.0, 'Min Nutrition': 0}},
 'foods': {u'chicken': {'Cost': 2.89},
  u'fries': {'Cost': 1.89},
  u'hamburger': {'Cost': 2.49},
  u'hot dog': {'Cost': 1.5},
  u'ice cream': {'Cost': 1.59},
  u'macaroni': {'Cost': 2.09},
  u'milk': {'Cost': 0.89},
  u'pizza': {'Cost': 1.99},
  u'salad': {'Cost': 2.49}}, 'nutrition_quantities': {
  (u'chicken', u'calories'): {'Quantity': 420},
  (u'chicken', u'fat'): {'Quantity': 10},
  (u'chicken', u'protein'): {'Quantity': 32},
  (u'chicken', u'sodium'): {'Quantity': 1190},
  (u'fries', u'calories'): {'Quantity': 380},
  (u'fries', u'fat'): {'Quantity': 19},
  (u'fries', u'protein'): {'Quantity': 4},
  (u'fries', u'sodium'): {'Quantity': 270},
  (u'hamburger', u'calories'): {'Quantity': 410},
  (u'hamburger', u'fat'): {'Quantity': 26},
  (u'hamburger', u'protein'): {'Quantity': 24},
  (u'hamburger', u'sodium'): {'Quantity': 730},
  (u'hot dog', u'calories'): {'Quantity': 560},
  (u'hot dog', u'fat'): {'Quantity': 32},
  (u'hot dog', u'protein'): {'Quantity': 20},
  (u'hot dog', u'sodium'): {'Quantity': 1800},
  (u'ice cream', u'calories'): {'Quantity': 330},
  (u'ice cream', u'fat'): {'Quantity': 10},
  (u'ice cream', u'protein'): {'Quantity': 8},
  (u'ice cream', u'sodium'): {'Quantity': 180},
  (u'macaroni', u'calories'): {'Quantity': 320},
  (u'macaroni', u'fat'): {'Quantity': 10},
  (u'macaroni', u'protein'): {'Quantity': 12},
  (u'macaroni', u'sodium'): {'Quantity': 930},
  (u'milk', u'calories'): {'Quantity': 100},
  (u'milk', u'fat'): {'Quantity': 2.5},
  (u'milk', u'protein'): {'Quantity': 8},
  (u'milk', u'sodium'): {'Quantity': 125},
  (u'pizza', u'calories'): {'Quantity': 320},
  (u'pizza', u'fat'): {'Quantity': 12},
  (u'pizza', u'protein'): {'Quantity': 15},
  (u'pizza', u'sodium'): {'Quantity': 820},
  (u'salad', u'calories'): {'Quantity': 320},
  (u'salad', u'fat'): {'Quantity': 12},
  (u'salad', u'protein'): {'Quantity': 31},
  (u'salad', u'sodium'): {'Quantity': 1230}}})
_diet_sln_tdf = TicDatFactory(
    parameters = [["Key"],["Value"]],
    buy_food = [["Food"],["Quantity"]],
    consume_nutrition = [["Category"],["Quantity"]])
_diet_sln_ticdat = _diet_sln_tdf.TicDat(**{'buy_food': {
  u'hamburger': {'Quantity': 0.604513888889},
  u'ice cream': {'Quantity': 2.59131944444},
  u'milk': {'Quantity': 6.97013888889}},
 'consume_nutrition': {
  u'calories': {'Quantity': 1800},
  u'fat': {'Quantity': 59.0559027778},
  u'protein': {'Quantity': 91},
  u'sodium': {'Quantity': 1779}},
 'parameters': {u'Total Cost': {'Value': 11.8288611111}}})

_netflow_mod = """
    set NODES;
    set ARCS within {i in NODES, j in NODES: i <> j};
    set COMMODITIES;
    param capacity {ARCS} >= 0;
    param cost {COMMODITIES,ARCS} > 0;
    param inflow {COMMODITIES,NODES};
    var Flow {COMMODITIES,ARCS} >= 0;
    minimize TotalCost:
       sum {h in COMMODITIES, (i,j) in ARCS} cost[h,i,j] * Flow[h,i,j];
    subject to Capacity {(i,j) in ARCS}:
       sum {h in COMMODITIES} Flow[h,i,j] <= capacity[i,j];
    subject to Conservation {h in COMMODITIES, j in NODES}:
       sum {(i,j) in ARCS} Flow[h,i,j] + inflow[h,j] = sum {(j,i) in ARCS} Flow[h,j,i];
"""
_netflow_input_tdf = TicDatFactory(
    commodities=[["Name"], []],
    nodes=[["Name"], []],
    arcs=[["Source", "Destination"], ["Capacity"]],
    cost=[["Commodity", "Source", "Destination"], ["Cost"]],
    inflow=[["Commodity", "Node"], ["Quantity"]]
)
_netflow_dat = _netflow_input_tdf.TicDat(**
{'arcs': {(u'Denver', u'Boston'): {'Capacity': 120.0},
  (u'Denver', u'New York'): {'Capacity': 120.0},
  (u'Denver', u'Seattle'): {'Capacity': 120.0},
  (u'Detroit', u'Boston'): {'Capacity': 100.0},
  (u'Detroit', u'New York'): {'Capacity': 80.0},
  (u'Detroit', u'Seattle'): {'Capacity': 120.0}},
 'commodities': {u'Pencils': {}, u'Pens': {}},
 'cost': {(u'Pencils', u'Denver', u'Boston'): {'Cost': 40},
  (u'Pencils', u'Denver', u'New York'): {'Cost': 40},
  (u'Pencils', u'Denver', u'Seattle'): {'Cost': 30},
  (u'Pencils', u'Detroit', u'Boston'): {'Cost': 10},
  (u'Pencils', u'Detroit', u'New York'): {'Cost': 20},
  (u'Pencils', u'Detroit', u'Seattle'): {'Cost': 60},
  (u'Pens', u'Denver', u'Boston'): {'Cost': 60},
  (u'Pens', u'Denver', u'New York'): {'Cost': 70},
  (u'Pens', u'Denver', u'Seattle'): {'Cost': 30},
  (u'Pens', u'Detroit', u'Boston'): {'Cost': 20},
  (u'Pens', u'Detroit', u'New York'): {'Cost': 20},
  (u'Pens', u'Detroit', u'Seattle'): {'Cost': 80}},
 'inflow': {(u'Pencils', u'Boston'): {'Quantity': -50},
  (u'Pencils', u'Denver'): {'Quantity': 60},
  (u'Pencils', u'Detroit'): {'Quantity': 50},
  (u'Pencils', u'New York'): {'Quantity': -50},
  (u'Pencils', u'Seattle'): {'Quantity': -10},
  (u'Pens', u'Boston'): {'Quantity': -40},
  (u'Pens', u'Denver'): {'Quantity': 40},
  (u'Pens', u'Detroit'): {'Quantity': 60},
  (u'Pens', u'New York'): {'Quantity': -30},
  (u'Pens', u'Seattle'): {'Quantity': -30}},
 'nodes': {u'Boston': {},
  u'Denver': {},
  u'Detroit': {},
  u'New York': {},
  u'Seattle': {}}})


_netflow_sln_tdf = TicDatFactory(
        flow = [["Commodity", "Source", "Destination"], ["Quantity"]],
        parameters = [["Key"],["Value"]])
_netflow_sln_ticdat = _netflow_sln_tdf.TicDat(**{'flow': {
  (u'Pencils', u'Denver', u'New York'): {'Quantity': 50},
  (u'Pencils', u'Denver', u'Seattle'): {'Quantity': 10},
  (u'Pencils', u'Detroit', u'Boston'): {'Quantity': 50},
  (u'Pens', u'Denver', u'Boston'): {'Quantity': 10},
  (u'Pens', u'Denver', u'Seattle'): {'Quantity': 30},
  (u'Pens', u'Detroit', u'Boston'): {'Quantity': 30},
  (u'Pens', u'Detroit', u'New York'): {'Quantity': 30}},
 'parameters': {u'Total Cost': {'Value': 5500}}}
)

#@fail_to_debugger
class TestAmpl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._original_value = utils.development_deployed_environment
        utils.development_deployed_environment = True
    @classmethod
    def tearDownClass(cls):
        utils.development_deployed_environment = cls._original_value

    def test_diet_amplpy(self):
        dat = _diet_input_tdf.copy_to_ampl(_diet_dat, field_renamings={("foods", "Cost"): "cost",
                ("categories", "Min Nutrition"): "n_min", ("categories", "Max Nutrition"): "n_max",
                ("nutrition_quantities", "Quantity"): "amt",
                ("nutrition_quantities", "Other Quantity"): "other_amt"})
        self.assertTrue({"n_min", "n_max"}.issubset(dat.categories.toPandas().columns))
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.eval(_diet_mod)
        _diet_input_tdf.set_ampl_data(dat, ampl, {"categories": "CAT", "foods": "FOOD"})
        ampl.solve()

        sln = _diet_sln_tdf.copy_from_ampl_variables(
            {("buy_food", "Quantity"):ampl.getVariable("Buy"),
            ("consume_nutrition", "Quantity"):ampl.getVariable("Consume")})
        sln.parameters['Total Cost'] = ampl.getObjective('Total_Cost').value()

        diet_dat_two = _diet_input_tdf.copy_tic_dat(_diet_dat)
        for r in diet_dat_two.nutrition_quantities.values():
            r["Quantity"], r["Other Quantity"] = [0.5 * r["Quantity"]] * 2

        dat = _diet_input_tdf.copy_to_ampl(diet_dat_two, field_renamings={("foods", "Cost"): "cost",
                ("categories", "Min Nutrition"): "n_min", ("categories", "Max Nutrition"): "n_max",
                ("nutrition_quantities", "Quantity"): "amt",
                ("nutrition_quantities", "Other Quantity"): "other_amt"})
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.eval(_diet_mod)
        _diet_input_tdf.set_ampl_data(dat, ampl, {"categories": "CAT", "foods": "FOOD"})
        ampl.solve()
        self.assertTrue("solved" == ampl.getValue("solve_result"))

        sln = _diet_sln_tdf.copy_from_ampl_variables(
            {("buy_food", "Quantity"):ampl.getVariable("Buy"),
            ("consume_nutrition", "Quantity"):ampl.getVariable("Consume")})
        sln.parameters['Total Cost'] = ampl.getObjective('Total_Cost').value()

        self.assertTrue(_nearly_same_dat(_diet_sln_tdf, sln, _diet_sln_ticdat))

        dat = _diet_input_tdf.copy_to_ampl(_diet_dat, {("foods", "Cost"): "cost",
                ("categories", "Min Nutrition"): "", ("categories", "Max Nutrition"): "n_max"},
                ["nutrition_quantities"])
        self.assertFalse(hasattr(dat, "nutrition_quantities"))
        self.assertTrue({"n_min", "n_max"}.intersection(dat.categories.toPandas().columns) == {"n_max"})

        sln_tdf_2  = TicDatFactory(buy_food = [["Food"],["Quantity"]],
                                   consume_nutrition = [["Category"],[]])
        sln_tdf_2.set_default_value("buy_food", "Quantity", 1)
        sln_2 = sln_tdf_2.copy_from_ampl_variables(
            {("buy_food", False):ampl.getVariable("Buy"),
             ("consume_nutrition",False):(ampl.getVariable("Consume"), lambda x : x < 100)})
        self.assertTrue(set(sln_2.buy_food) == set(sln.buy_food) and
                        all(v["Quantity"] == 1 for v in sln_2.buy_food.values()))
        self.assertTrue(sln_2.consume_nutrition and set(sln_2.consume_nutrition) ==
                        {k for k,v in sln.consume_nutrition.items() if v["Quantity"] < 100})

        diet_dat_two = _diet_input_tdf.copy_tic_dat(_diet_dat)
        diet_dat_two.categories["calories"] = [0,200]
        dat = _diet_input_tdf.copy_to_ampl(diet_dat_two, field_renamings={("foods", "Cost"): "cost",
                ("categories", "Min Nutrition"): "n_min", ("categories", "Max Nutrition"): "n_max",
                ("nutrition_quantities", "Quantity"): "amt",
                ("nutrition_quantities", "Other Quantity"): "other_amt"})
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.eval(_diet_mod)
        _diet_input_tdf.set_ampl_data(dat, ampl, {"categories": "CAT", "foods": "FOOD"})
        ampl.solve()
        self.assertTrue("infeasible" == ampl.getValue("solve_result"))

        diet_dat_two = _diet_input_tdf.copy_tic_dat(_diet_dat)
        for v in diet_dat_two.categories.values():
            v["Max Nutrition"] = float("inf")
        diet_dat_two.foods["hamburger"] = -1
        dat = _diet_input_tdf.copy_to_ampl(diet_dat_two, field_renamings={("foods", "Cost"): "cost",
                ("categories", "Min Nutrition"): "n_min", ("categories", "Max Nutrition"): "n_max",
                ("nutrition_quantities", "Quantity"): "amt",
                ("nutrition_quantities", "Other Quantity"): "other_amt"})
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.eval(_diet_mod)
        _diet_input_tdf.set_ampl_data(dat, ampl, {"categories": "CAT", "foods": "FOOD"})
        ampl.solve()
        self.assertTrue("unbounded" == ampl.getValue("solve_result"))

    def test_netflow_amplpy(self):
        dat = _netflow_input_tdf.copy_to_ampl(_netflow_dat, field_renamings={("arcs", "Capacity"): "capacity",
            ("cost", "Cost"): "cost", ("inflow", "Quantity"): "inflow"})
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.eval(_netflow_mod)
        _netflow_input_tdf.set_ampl_data(dat, ampl, {"nodes": "NODES", "arcs": "ARCS",
                                           "commodities": "COMMODITIES"})
        ampl.solve()

        sln = _netflow_sln_tdf.copy_from_ampl_variables(
            {('flow' ,'Quantity'):ampl.getVariable("Flow")})
        sln.parameters["Total Cost"] = ampl.getObjective('TotalCost').value()

        self.assertTrue(_nearly_same_dat(_netflow_sln_tdf, sln, _netflow_sln_ticdat))

        sln2 = _netflow_sln_tdf.copy_from_ampl_variables(
            {('flow' ,'Quantity'):(ampl.getVariable("Flow"), lambda v : v>30)})
        sln3 = _netflow_sln_tdf.copy_from_ampl_variables(
            {('flow' ,'Quantity'):(ampl.getVariable("Flow"), lambda v : 0<v<=30)})
        sln2.parameters["Total Cost"] = sln3.parameters["Total Cost"] = sln.parameters["Total Cost"]

        self.assertTrue(sln2.flow and sln3.flow)
        self.assertFalse(_nearly_same_dat(_netflow_sln_tdf, sln, sln2))
        self.assertFalse(_nearly_same_dat(_netflow_sln_tdf, sln, sln3))
        for k,v in sln3.flow.items():
            sln2.flow[k] = v
        self.assertTrue(_nearly_same_dat(_netflow_sln_tdf, sln, sln2))

if __name__ == "__main__":
    if not amplpy:
        print("!!!testampl.py is going to fail because amplpy is not installed!!!")
    unittest.main()