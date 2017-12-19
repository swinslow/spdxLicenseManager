testft:
	python -m unittest discover -s tests -p "ft_*.py"

testunit:
	python -m unittest discover -s tests -p "unit_*.py"

.PHONY: testft testunit test
