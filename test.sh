#!/bin/bash
_fastTests()
{
	python -m unittest test.BooleanSemanticsTest test.QuantitativeSemanticsTest
}

_cartPoleTests()
{
	python -m unittest test.BooleanCartpoleTest test.QuantitativeCartpoleTest
}

_allTests()
{
	python -m unittest test.BooleanSemanticsTest test.QuantitativeSemanticsTest test.BooleanCartpoleTest test.QuantitativeCartpoleTest
}


cd "$(dirname "$0")"
if [[ $# == 0 ]]; then
	echo 'Test script initialized with no parameters.'
	echo 'Running fast tests...'
	set -- 'fast'
fi
if [[ $1 == 'all' ]]; then 
	echo 'Running all tests...'
	_allTests
elif [[ $1 == 'cartpole' ]]; then
	echo 'Running only the cartpole (slow) tests...'
	_cartPoleTests
elif [[ $1 == 'fast' ]]; then
	echo 'Running only the fast tests...'
	_fastTests
else
	echo 'Unknown parameter passed.'
fi
