{{
  config(
    materialized = 'view',
    tags = ['silver', 'ventes']
  )
}}

-- Grain : une commande, dans son état courant.
-- L'ordre d'autorité est source_version, jamais event_ts ni ingested_at :
-- un événement ancien arrivé en dernier ne doit pas écraser un état plus récent.

with versions as (

    select
        order_id,
        customer_id,
        store_id,
        channel,
        cast(order_ts as timestamp)        as order_ts,
        status,
        currency,
        campaign_id,
        cast(order_discount as decimal(18, 4)) as order_discount,
        op,
        cast(source_version as bigint)     as source_version,
        cast(event_ts as timestamp)        as event_ts,
        batch_id

    from {{ source('bronze', 'orders') }}

),

derniere_version as (

    select
        *,
        row_number() over (
            partition by order_id
            order by source_version desc
        ) as rang

    from versions

)

select
    order_id,
    customer_id,
    store_id,
    channel,
    order_ts,
    status,
    currency,
    campaign_id,
    order_discount,
    source_version,
    event_ts,
    batch_id,
    -- Une suppression CDC est un tombstone : la ligne reste visible ici et
    -- l'exclusion est décidée en aval, de façon explicite et testable.
    op = 'D' as est_supprime

from derniere_version
where rang = 1
