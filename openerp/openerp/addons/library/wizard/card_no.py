

from openerp.osv import osv,fields

class card_number(osv.TransientModel):
    
    _name="card.number"
    _description="Card Number"
    _columns={
                'card_id': fields.many2one("library.card", "Card No", required=True), 
              }
    
    def card_number_ok(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        lib_book_obj = self.pool.get('library.book.issue')
        for rec in self.browse(cr,uid,ids,context=context):
                search_card_ids =lib_book_obj.search(cr,uid,[('card_id', '=', rec.card_id.id)],context=context)
                if not search_card_ids:
                        raise osv.except_osv(('Warning !'),('Invalid Card Number.'))
                else:
                    
                    return {'type': 'ir.actions.act_window',
                            'res_model':'book.name',
                            'src_model':'library.book.issue',
                            'target':'new',
                            'view_mode':'form',
                            'view_type':'form',
                            'context' : {'default_card_id' : rec.card_id.id}
                            }
    
card_number()