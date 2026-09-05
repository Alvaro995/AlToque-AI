-- Roles
CREATE TYPE public.app_role AS ENUM ('paciente', 'cuidador');

-- Profiles
CREATE TABLE public.profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name text NOT NULL DEFAULT '',
  role public.app_role NOT NULL DEFAULT 'paciente',
  avatar text NOT NULL DEFAULT '🙂',
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE ON public.profiles TO authenticated;
GRANT ALL ON public.profiles TO service_role;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Care links
CREATE TABLE public.care_links (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id uuid NOT NULL,
  caregiver_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (patient_id, caregiver_id)
);
GRANT SELECT, DELETE ON public.care_links TO authenticated;
GRANT ALL ON public.care_links TO service_role;
ALTER TABLE public.care_links ENABLE ROW LEVEL SECURITY;

CREATE OR REPLACE FUNCTION public.is_linked(_a uuid, _b uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.care_links
    WHERE (patient_id = _a AND caregiver_id = _b)
       OR (patient_id = _b AND caregiver_id = _a)
  )
$$;

CREATE POLICY "read own or linked profile" ON public.profiles
  FOR SELECT TO authenticated
  USING (id = auth.uid() OR public.is_linked(id, auth.uid()));
CREATE POLICY "insert own profile" ON public.profiles
  FOR INSERT TO authenticated WITH CHECK (id = auth.uid());
CREATE POLICY "update own profile" ON public.profiles
  FOR UPDATE TO authenticated USING (id = auth.uid());

CREATE POLICY "read own links" ON public.care_links
  FOR SELECT TO authenticated
  USING (patient_id = auth.uid() OR caregiver_id = auth.uid());
CREATE POLICY "delete own links" ON public.care_links
  FOR DELETE TO authenticated
  USING (patient_id = auth.uid() OR caregiver_id = auth.uid());

-- Invite codes
CREATE TABLE public.invite_codes (
  code text PRIMARY KEY,
  patient_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL DEFAULT now() + interval '1 day'
);
GRANT SELECT, INSERT, DELETE ON public.invite_codes TO authenticated;
GRANT ALL ON public.invite_codes TO service_role;
ALTER TABLE public.invite_codes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "manage own invite codes" ON public.invite_codes
  FOR ALL TO authenticated
  USING (patient_id = auth.uid()) WITH CHECK (patient_id = auth.uid());

CREATE OR REPLACE FUNCTION public.redeem_invite(_code text)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  _patient uuid;
BEGIN
  SELECT patient_id INTO _patient FROM public.invite_codes
   WHERE code = _code AND expires_at > now();
  IF _patient IS NULL THEN
    RAISE EXCEPTION 'Código inválido o vencido';
  END IF;
  IF _patient = auth.uid() THEN
    RAISE EXCEPTION 'No puedes vincularte contigo mismo';
  END IF;
  INSERT INTO public.care_links (patient_id, caregiver_id)
  VALUES (_patient, auth.uid())
  ON CONFLICT (patient_id, caregiver_id) DO NOTHING;
  RETURN _patient;
END;
$$;
GRANT EXECUTE ON FUNCTION public.redeem_invite(text) TO authenticated;

-- Events timeline
CREATE TABLE public.events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id uuid NOT NULL,
  kind text NOT NULL DEFAULT 'otro',
  label text NOT NULL,
  detail text NOT NULL DEFAULT '',
  points integer NOT NULL DEFAULT 0,
  tone text NOT NULL DEFAULT 'ok',
  occurred_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, DELETE ON public.events TO authenticated;
GRANT ALL ON public.events TO service_role;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "read own or linked events" ON public.events
  FOR SELECT TO authenticated
  USING (patient_id = auth.uid() OR public.is_linked(patient_id, auth.uid()));
CREATE POLICY "insert own events" ON public.events
  FOR INSERT TO authenticated WITH CHECK (patient_id = auth.uid());
CREATE POLICY "delete own events" ON public.events
  FOR DELETE TO authenticated USING (patient_id = auth.uid());

-- Health profile
CREATE TABLE public.health_profiles (
  user_id uuid PRIMARY KEY,
  hba1c text,
  fasting text,
  work_start text,
  work_end text,
  notes text,
  updated_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE ON public.health_profiles TO authenticated;
GRANT ALL ON public.health_profiles TO service_role;
ALTER TABLE public.health_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "read own or linked health" ON public.health_profiles
  FOR SELECT TO authenticated
  USING (user_id = auth.uid() OR public.is_linked(user_id, auth.uid()));
CREATE POLICY "insert own health" ON public.health_profiles
  FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
CREATE POLICY "update own health" ON public.health_profiles
  FOR UPDATE TO authenticated USING (user_id = auth.uid());

-- Routine sheet
CREATE TABLE public.routines (
  user_id uuid PRIMARY KEY,
  items jsonb NOT NULL DEFAULT '[]'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE ON public.routines TO authenticated;
GRANT ALL ON public.routines TO service_role;
ALTER TABLE public.routines ENABLE ROW LEVEL SECURITY;
CREATE POLICY "read own or linked routine" ON public.routines
  FOR SELECT TO authenticated
  USING (user_id = auth.uid() OR public.is_linked(user_id, auth.uid()));
CREATE POLICY "insert own routine" ON public.routines
  FOR INSERT TO authenticated WITH CHECK (user_id = auth.uid());
CREATE POLICY "update own routine" ON public.routines
  FOR UPDATE TO authenticated USING (user_id = auth.uid());

-- Chat history
CREATE TABLE public.chat_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  role text NOT NULL,
  content text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, DELETE ON public.chat_messages TO authenticated;
GRANT ALL ON public.chat_messages TO service_role;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own chat" ON public.chat_messages
  FOR ALL TO authenticated
  USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

-- Nudges (caregiver -> patient)
CREATE TABLE public.nudges (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id uuid NOT NULL,
  sender_id uuid NOT NULL,
  message text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  seen boolean NOT NULL DEFAULT false
);
GRANT SELECT, INSERT, UPDATE ON public.nudges TO authenticated;
GRANT ALL ON public.nudges TO service_role;
ALTER TABLE public.nudges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "read own or linked nudges" ON public.nudges
  FOR SELECT TO authenticated
  USING (patient_id = auth.uid() OR sender_id = auth.uid());
CREATE POLICY "send nudges to linked" ON public.nudges
  FOR INSERT TO authenticated
  WITH CHECK (sender_id = auth.uid() AND public.is_linked(patient_id, auth.uid()));
CREATE POLICY "patient marks seen" ON public.nudges
  FOR UPDATE TO authenticated USING (patient_id = auth.uid());

-- Profile bootstrap
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, role)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data ->> 'full_name', ''),
    COALESCE((NEW.raw_user_meta_data ->> 'role')::public.app_role, 'paciente')
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Realtime
ALTER TABLE public.events REPLICA IDENTITY FULL;
ALTER TABLE public.nudges REPLICA IDENTITY FULL;
ALTER TABLE public.care_links REPLICA IDENTITY FULL;
ALTER PUBLICATION supabase_realtime ADD TABLE public.events;
ALTER PUBLICATION supabase_realtime ADD TABLE public.nudges;
ALTER PUBLICATION supabase_realtime ADD TABLE public.care_links;
