# IOT Thermostat backend

This is an AnyBlok backend to store desired and current states of the
applications.

# add fuele gauge metric

```python
>>> registry.commit()
>>> from datetime import datetime
>>> jauge = registry.Iot.Device.query().filter_by(code="FUEL").one()
>>> date = datetime(2012, 10, 5, 22, 00)
>>> registry.Iot.State.FuelGauge.insert(level=815, device=jauge, create_date=date, edit_date=date)
```
