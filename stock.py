# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Stock Move Ext
#    Copyright (C) 2013 Enterprise Objects Consulting
#                       http://www.eoconsulting.com.ar
#    Authors: Mariano Ruiz <mrsarm@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields, osv
from tools.translate import _

import time

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        for move in self.browse(cr, uid, ids, context=context):
            if move.state != 'draft' and move.state != 'waiting' and move.state != 'confirmed' and not ctx.get('call_unlink',False):
                raise osv.except_osv(_('UserError'),
                        _('You can only delete draft moves.'))
        return osv.osv.unlink(self, cr, uid, ids, context=ctx)

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, address_id=False):
        result = super(stock_move,self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, address_id)
        if result == {} or 'name' in result['value']:
            return result
        ctx = {'lang': self._get_lang(cr, uid, address_id)}
        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        product_name = ''
        if product.default_code:
            product_name += '[' + product.default_code + '] '
        product_name += product.name
        result['value']['name'] = product_name
        return result

    def _get_lang(self, cr, uid, address_id):
        lang = False
        if address_id:
            addr_rec = self.pool.get('res.partner.address').browse(cr, uid, address_id)
            if addr_rec:
                lang = addr_rec.partner_id and addr_rec.partner_id.lang or False
        return lang

    # Override this function to make partner_id = None
    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given stock move.
        """
        # prepare default values considering that the destination accounts have the reference_currency_id as their main currency
        #partner_id = (move.picking_id.address_id and move.picking_id.address_id.partner_id and move.picking_id.address_id.partner_id.id) or False
        partner_id = False
        debit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id and move.product_id.id or False,
                    'quantity': move.product_qty,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': partner_id,
                    'debit': reference_amount,
                    'account_id': dest_account_id,
        }
        credit_line_vals = {
                    'name': move.name,
                    'product_id': move.product_id and move.product_id.id or False,
                    'quantity': move.product_qty,
                    'ref': move.picking_id and move.picking_id.name or False,
                    'date': time.strftime('%Y-%m-%d'),
                    'partner_id': partner_id,
                    'credit': reference_amount,
                    'account_id': src_account_id,
        }

        # if we are posting to accounts in a different currency, provide correct values in both currencies correctly
        # when compatible with the optional secondary currency on the account.
        # Financial Accounts only accept amounts in secondary currencies if there's no secondary currency on the account
        # or if it's the same as that of the secondary amount being posted.
        account_obj = self.pool.get('account.account')
        src_acct, dest_acct = account_obj.browse(cr, uid, [src_account_id, dest_account_id], context=context)
        src_main_currency_id = src_acct.company_id.currency_id.id
        dest_main_currency_id = dest_acct.company_id.currency_id.id
        cur_obj = self.pool.get('res.currency')
        if reference_currency_id != src_main_currency_id:
            # fix credit line:
            credit_line_vals['credit'] = cur_obj.compute(cr, uid, reference_currency_id, src_main_currency_id, reference_amount, context=context)
            if (not src_acct.currency_id) or src_acct.currency_id.id == reference_currency_id:
                credit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)
        if reference_currency_id != dest_main_currency_id:
            # fix debit line:
            debit_line_vals['debit'] = cur_obj.compute(cr, uid, reference_currency_id, dest_main_currency_id, reference_amount, context=context)
            if (not dest_acct.currency_id) or dest_acct.currency_id.id == reference_currency_id:
                debit_line_vals.update(currency_id=reference_currency_id, amount_currency=reference_amount)

        return [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

stock_move()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _set_maximum_date(self, cr, uid, ids, name, value, arg, context=None):
        """ Calculates planned date if it is greater than 'value'.
        @param name: Name of field
        @param value: Value of field
        @param arg: User defined argument
        @return: True or False
        """
        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]
        for pick in self.browse(cr, uid, ids, context=context):
            sql_str = """update stock_move set
                    date='%(date)s', date_expected='%(date)s'
                where
                    picking_id=%(pick_id)d """ % {'date': value, 'pick_id': pick.id}

            if pick.max_date:
                sql_str += " and (date='" + pick.max_date + "' or date>'" + value + "' or date_expected>'" + value + "')"
            cr.execute(sql_str)
        return True

    def _set_minimum_date(self, cr, uid, ids, name, value, arg, context=None):
        """ Calculates planned date if it is less than 'value'.
        @param name: Name of field
        @param value: Value of field
        @param arg: User defined argument
        @return: True or False
        """
        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]
        for pick in self.browse(cr, uid, ids, context=context):
            sql_str = """update stock_move set
                    date='%(date)s', date_expected='%(date)s'
                where
                    picking_id=%(pick_id)d """ % {'date': value, 'pick_id': pick.id}
            if pick.min_date:
                sql_str += " and (date='" + pick.min_date + "' or date<'" + value + "' or date_expected<'" + value + "')"
            cr.execute(sql_str)
        return True

    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        return super(stock_picking,self).get_min_max_date(cr, uid, ids, field_name, arg, context)

    # Override order by Order Date (desc) in list view
    _order = 'date desc, id'

    # Override the min/max dates function fields
    _columns = {
        'min_date': fields.function(get_min_max_date, fnct_inv=_set_minimum_date, multi="min_max_date",
                 store=True, type='datetime', string='Expected Date', select=1, help="Expected date for the picking to be processed"),
        'max_date': fields.function(get_min_max_date, fnct_inv=_set_maximum_date, multi="min_max_date",
                 store=True, type='datetime', string='Max. Expected Date', select=2),
    }

    _defaults = {
        'move_type': lambda s,c,u,ctx: s.pool.get('sale.order').default_get(c,u,['picking_policy'],context=ctx)['picking_policy']
    }

    def action_assign(self, cr, uid, ids, *args):
        """ Changes state of picking to available if all moves are confirmed.
        @return: True
        """
        for pick in self.browse(cr, uid, ids):
            move_ids = [x.id for x in pick.move_lines if x.state == 'confirmed']
            if not move_ids:
                raise osv.except_osv(_('Warning !'), \
                    _('Not enough stock, unable to reserve the products.\n' \
                      'Check if all moves in this order are in Confirmed or Available state.'))
            self.pool.get('stock.move').action_assign(cr, uid, move_ids)
        return True

    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        if not isinstance(ids, list):
            ids = [ids]
        if len(ids)==1 and group==True:
            # To prevent invoice line with **[OUT CODE]-**Product description
            group=False
        return super(stock_picking,self).action_invoice_create(cr, uid, ids, journal_id, group, type, context)

stock_picking()
