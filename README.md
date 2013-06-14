Stock Move Extension
====================

This OpenERP module improve the Stock Picking and Stock Move features. 

Enhancements:

 * Allow users to delete stock move when state != draft.
 * Fix the update of min/max date and expected date in
   calendar view of Stock Picking
 * Fix when a product is changed in a stock move, the
   description is updated too
 * Better message exceptions
 * Take default "Delivery Method" in Picking from default "Picking Policy"
   (configurable by "Setup Picking Policy" wizard)
 * Better translation to Spanish (es) and Spanish (AR)
 * Override order by Order Date (desc) in list view
 * In real time stock valuation, remove the partner in the journal items,
   preventing noise in the partner customer credit / supplier debit.
 * Currently in development ...

Only tested with *OpenERP v6.1*.

Authors:

    Mariano Ruiz <mrsarm@gmail.com> (Enterprise Objects Consulting)

This sources are available in https://github.com/eoconsulting/stock_move_ext

License: AGPL-3
(C) 2013

__________

[Enterprise Objects Consulting](http://www.eoconsulting.com.ar)
