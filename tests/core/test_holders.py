# -*- coding: utf-8 -*-

import numpy as np
from nose.tools import assert_equal, assert_items_equal, assert_is_none

from openfisca_core.simulations import Simulation
from openfisca_core.periods import period, ETERNITY
from openfisca_core.tools import assert_near
from openfisca_core.memory_config import MemoryConfig
from openfisca_country_template.situation_examples import single
from test_countries import tax_benefit_system

force_storage_on_disk = MemoryConfig(max_memory_occupation = 0)


def get_simulation(**kwargs):
    return Simulation(tax_benefit_system = tax_benefit_system, simulation_json = single, **kwargs)


def test_permanent_variable_empty():
    simulation = get_simulation()
    holder = simulation.person.get_holder('birth')
    assert_is_none(holder.get_array(None))


def test_permanent_variable_filled():
    simulation = get_simulation()
    holder = simulation.person.get_holder('birth')
    value = np.asarray(['1980-01-01'], dtype = holder.variable.dtype)
    holder.set_input(period(ETERNITY), value)
    assert_equal(holder.get_array(None), value)
    assert_equal(holder.get_array(ETERNITY), value)
    assert_equal(holder.get_array('2016-01'), value)


def test_delete_arrays():
    simulation = get_simulation()
    salary_holder = simulation.person.get_holder('salary')
    salary_holder.set_input(period(2017), np.asarray([30000]))
    salary_holder.set_input(period(2018), np.asarray([60000]))
    assert_equal(simulation.person('salary', '2017-01'), 2500)
    assert_equal(simulation.person('salary', '2018-01'), 5000)
    salary_holder.delete_arrays(period = 2018)
    salary_holder.set_input(period(2018), np.asarray([15000]))
    assert_equal(simulation.person('salary', '2017-01'), 2500)
    assert_equal(simulation.person('salary', '2018-01'), 1250)


def test_get_memory_usage():
    simulation = get_simulation()
    salary_holder = simulation.person.get_holder('salary')
    memory_usage = salary_holder.get_memory_usage()
    assert_equal(memory_usage['total_nb_bytes'], 0)
    salary_holder.set_input(period(2017), np.asarray([30000]))
    memory_usage = salary_holder.get_memory_usage()
    assert_equal(memory_usage['nb_cells_by_array'], 1)
    assert_equal(memory_usage['cell_size'], 4)  # float 32
    assert_equal(memory_usage['nb_cells_by_array'], 1)  # one person
    assert_equal(memory_usage['nb_arrays'], 12)  # 12 months
    assert_equal(memory_usage['total_nb_bytes'], 4 * 12 * 1)


def test_delete_arrays_on_disk():
    simulation = get_simulation(memory_config = force_storage_on_disk)  # Force using disk
    salary_holder = simulation.person.get_holder('salary')
    salary_holder.set_input(period(2017), np.asarray([30000]))
    salary_holder.set_input(period(2018), np.asarray([60000]))
    assert_equal(simulation.person('salary', '2017-01'), 2500)
    assert_equal(simulation.person('salary', '2018-01'), 5000)
    salary_holder.delete_arrays(period = 2018)
    salary_holder.set_input(period(2018), np.asarray([15000]))
    assert_equal(simulation.person('salary', '2017-01'), 2500)
    assert_equal(simulation.person('salary', '2018-01'), 1250)


def test_cache_disk():
    simulation = get_simulation(memory_config = force_storage_on_disk)  # Force using disk
    month = period('2017-01')
    holder = simulation.person.get_holder('salary')
    data = np.asarray([2000, 3000, 0, 500])
    holder.put_in_cache(data, month)
    stored_data = holder.get_array(month)
    assert_near(data, stored_data)


def test_cache_disk_with_extra_params():
    simulation = get_simulation(memory_config = force_storage_on_disk)  # Force using disk
    month = period('2017-01')
    extra_param_1 = period('2017-02')
    extra_param_2 = period('2017-03')
    holder = simulation.person.get_holder('salary')
    data_1 = np.asarray([2000, 3000, 0, 500])
    data_2 = np.asarray([1000, 4000, 200, 200])
    holder.put_in_cache(data_1, month, extra_params = [extra_param_1])
    holder.put_in_cache(data_2, month, extra_params = [extra_param_2])
    stored_data_1 = holder.get_array(month, extra_params = [extra_param_1])
    stored_data_2 = holder.get_array(month, extra_params = [extra_param_2])
    assert_near(data_1, stored_data_1)
    assert_near(data_2, stored_data_2)


def test_known_periods():
    simulation = get_simulation(memory_config = force_storage_on_disk)  # Force using disk
    month = period('2017-01')
    month_2 = period('2017-02')
    holder = simulation.person.get_holder('salary')
    data = np.asarray([2000, 3000, 0, 500])
    holder.put_in_cache(data, month)
    holder._memory_storage.put(data, month_2)
    assert_items_equal(holder.get_known_periods(), [month, month_2])