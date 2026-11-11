-- Test métier : une remise de commande supérieure à la base des lignes
-- facturées rend l'allocation impossible. La commande doit être bloquée,
-- pas arrondie en silence (section 07).

with base_par_commande as (

    select
        order_id,
        sum(base_ht) as base_totale

    from {{ ref('stg_order_lines') }}
    where est_eligible_vente
    group by order_id

)

select
    o.order_id,
    o.order_discount,
    b.base_totale

from {{ ref('stg_orders') }} as o
inner join base_par_commande as b
    on o.order_id = b.order_id

where o.order_discount > b.base_totale
