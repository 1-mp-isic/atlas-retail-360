{% snapshot snp_crm_customers %}

{{
    config(
        target_schema = 'atlas_silver',
        unique_key = 'customer_id',
        strategy = 'timestamp',
        updated_at = 'updated_at',
        invalidate_hard_deletes = false
    )
}}

-- Le snapshot capture l'ÉTAT COURANT observé du CRM, rien de plus.
-- Il ne reconstitue pas les changements antérieurs à sa première capture, et
-- ne doit pas être présenté comme tel (section 12).
-- L'historique métier des segments vient de customer_segment_events.
--
-- invalidate_hard_deletes reste à false : une disparition du CRM n'est une
-- suppression que si le manifeste certifie un FULL complet (section 06).

select
    customer_id,
    country,
    segment,
    signup_date,
    cast(updated_at as timestamp) as updated_at

from {{ source('bronze', 'crm_customers') }}

{% endsnapshot %}
