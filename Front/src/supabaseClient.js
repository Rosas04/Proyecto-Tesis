import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://eytmbhfdjccvxmpjvidq.supabase.co/rest/v1/';
const SUPABASE_ANON_KEY = 'sb_publishable_qXcegNP8uHAsdRLtMykn0A_IpM270lj';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
