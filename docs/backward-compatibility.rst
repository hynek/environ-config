Backward Compatibility
======================

This project has a very strong backward compatibility policy that is inspired by the one of the `Twisted framework <https://twistedmatrix.com/trac/wiki/CompatibilityPolicy>`_.

Put simply, you shouldn't ever be afraid to upgrade if you're using its public APIs.

If there is the need to break compatibility:

1. It will be announced in the :doc:`changelog`,
2. a deprecation warning will be raised for a year,
3. backward compatibility will be finally broken no earlier than one year after step 1.
