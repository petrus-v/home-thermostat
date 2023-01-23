# IOT Thermostat backend

This is an AnyBlok backend to store desired and current states of the
applications.

# add fuele gauge metric

```python
from datetime import datetime
jauge = registry.Iot.Device.query().filter_by(code="FUEL").one()
date = datetime(2022, 11, 10, 22, 00)
registry.Iot.State.FuelGauge.insert(level=827, device=jauge, create_date=date, edit_date=date)
registry.commit()
```
